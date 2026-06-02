from __future__ import annotations

from typing import Any, Dict, List, Optional

from guaro.core.query_ir import QueryIR, RelationSelection
from guaro.db.adapters.base import DatabaseAdapter


class MemoryAdapter(DatabaseAdapter):
    """A simple in-memory adapter that stores model instances from the registry.

    This adapter expects the Guaro `Registry` to hold an in-memory store under
    `registry.serializers['store:<ModelName>']` which is the same mechanism used
    by `Model.save()` and `Model.all()` in the current MVP.
    """

    def __init__(self, registry: Any) -> None:
        self.registry = registry

    async def execute_query(self, ir: QueryIR) -> List[Dict[str, Any]]:
        store_key = f"store:{ir.entity}"
        store: List[Any] = self.registry.serializers.get(store_key, [])

        # Simple filter: only support equality filters (field, '==', value)
        results: List[Any] = []
        for item in store:
            match = True
            for (field, op, value) in ir.filters:
                val = getattr(item, field, None)
                if op == "==":
                    if val != value:
                        match = False
                        break
                else:
                    # unsupported op
                    match = False
                    break
            if match:
                results.append(item)

        # Projection: build dicts with requested fields
        projected: List[Dict[str, Any]] = []
        for item in results:
            row = {}
            for f in ir.fields or []:
                row[f] = getattr(item, f, None)
            # relations: simple nested for memory adapter
            for rel_name, rel_sel in ir.relations.items():
                rel_value = getattr(item, rel_name, None)
                if rel_value is None:
                    row[rel_name] = None
                elif isinstance(rel_value, list):
                    nested = []
                    for rel_item in rel_value:
                        nested_row = {}
                        for rf in rel_sel.fields:
                            nested_row[rf] = getattr(rel_item, rf, None)
                        nested.append(nested_row)
                    row[rel_name] = nested
                else:
                    nested_row = {}
                    for rf in rel_sel.fields:
                        nested_row[rf] = getattr(rel_value, rf, None)
                    row[rel_name] = nested_row

            projected.append(row)

        # pagination
        limit = ir.pagination.get("limit")
        offset = ir.pagination.get("offset", 0)
        if limit is not None:
            projected = projected[offset : offset + limit]
        elif offset:
            projected = projected[offset:]

        return projected

    async def insert(self, entity: str, data: Dict[str, Any]) -> Any:
        store_key = f"store:{entity}"
        store: List[Any] = self.registry.serializers.setdefault(store_key, [])
        # naive: create a simple object
        class O:
            pass

        obj = O()
        for k, v in data.items():
            setattr(obj, k, v)
        store.append(obj)
        return obj

    async def update(self, ir: QueryIR, data: Dict[str, Any]) -> Any:
        # naive: update first matching item
        rows = await self.execute_query(ir)
        if not rows:
            return None
        # find actual objects in store and update
        store_key = f"store:{ir.entity}"
        store: List[Any] = self.registry.serializers.get(store_key, [])
        updated = None
        for obj in store:
            match = True
            for (field, op, value) in ir.filters:
                val = getattr(obj, field, None)
                if op == "==":
                    if val != value:
                        match = False
                        break
            if match:
                for k, v in data.items():
                    setattr(obj, k, v)
                updated = obj
                break
        return updated

    async def delete(self, ir: QueryIR) -> int:
        # delete matching items and return count
        store_key = f"store:{ir.entity}"
        store: List[Any] = self.registry.serializers.get(store_key, [])
        to_remove = []
        for obj in store:
            match = True
            for (field, op, value) in ir.filters:
                val = getattr(obj, field, None)
                if op == "==":
                    if val != value:
                        match = False
                        break
            if match:
                to_remove.append(obj)
        for obj in to_remove:
            store.remove(obj)
        return len(to_remove)
