from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger("guaro.mongo")


class MongoAdapter:
    """Minimal MongoDB adapter using Motor (async).

    This adapter implements the same interface as other adapters used by the
    Repository: `execute_query`, `insert`, `update`, `delete`.
    """

    def __init__(self, registry: Any, url: str) -> None:
        self.registry = registry
        self.url = url
        self.client = None
        self.db = None

    async def connect(self) -> None:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("motor (async MongoDB driver) is required for MongoDB support") from exc

        self.client = AsyncIOMotorClient(self.url)
        # Use database name from URL path or default to 'guaro'
        # Motor client exposes 'get_default_database' if DB is in URL
        try:
            self.db = self.client.get_default_database() or self.client["guaro"]
        except Exception:
            self.db = self.client["guaro"]
        
        # Check auto_migrate setting (MongoDB is schema-less, so this is informational)
        cfg = getattr(self.registry, "db_config", None)
        auto_migrate = getattr(cfg, "auto_migrate", True) if cfg else True
        
        if auto_migrate:
            logger.debug("[Guaro Mongo] Connected (auto_migrate enabled)")
        else:
            logger.debug("[Guaro Mongo] Connected (auto_migrate disabled)")

    async def disconnect(self) -> None:
        if self.client is not None:
            self.client.close()
            logger.debug("[Guaro Mongo] Disconnected")

    def _collection_for(self, entity: str):
        return self.db[entity.lower()]

    async def execute_query(self, ir: Any) -> List[Dict[str, Any]]:
        coll = self._collection_for(ir.entity)
        # build filter
        q = {}
        for (field, op, value) in ir.filters:
            if op == "==":
                q[field] = value
        cursor = coll.find(q)
        if ir.pagination.get("limit") is not None:
            cursor = cursor.limit(ir.pagination.get("limit"))
        if ir.pagination.get("offset"):
            cursor = cursor.skip(ir.pagination.get("offset"))
        results = []
        async for doc in cursor:
            results.append(doc)
        return results

    async def insert(self, entity: str, data: Dict[str, Any]) -> Any:
        coll = self._collection_for(entity)
        res = await coll.insert_one(data)
        created = await coll.find_one({"_id": res.inserted_id})
        return created

    async def update(self, ir: Any, data: Dict[str, Any]) -> Any:
        coll = self._collection_for(ir.entity)
        q = {}
        for (field, op, value) in ir.filters:
            if op == "==":
                q[field] = value
        res = await coll.update_many(q, {"$set": data})
        return res.modified_count

    async def delete(self, ir: Any) -> int:
        coll = self._collection_for(ir.entity)
        q = {}
        for (field, op, value) in ir.filters:
            if op == "==":
                q[field] = value
        res = await coll.delete_many(q)
        return res.deleted_count
