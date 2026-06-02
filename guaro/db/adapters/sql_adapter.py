from __future__ import annotations

import logging
from typing import Any, Dict, List

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    select,
    insert as sa_insert,
    update as sa_update,
    delete as sa_delete,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from guaro.core.query_ir import QueryIR
from guaro.db.adapters.base import DatabaseAdapter

logger = logging.getLogger("guaro.sql")

PY_TYPE_MAP = {
    int: Integer,
    str: String,
    float: Float,
    bool: Boolean,
}


class SQLAdapter(DatabaseAdapter):
    def __init__(self, registry: Any, db_url: str) -> None:
        self.registry = registry
        self.db_url = db_url
        self.engine: AsyncEngine = create_async_engine(db_url, echo=False)
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}

        # lazily create tables dictionary for known models
        self._prepare_tables()

    def _prepare_tables(self) -> None:
        for name, meta in self.registry.models.items():
            table_name = name.lower()
            if table_name in self.tables:
                continue
            cols = []
            for fname, fmeta in meta.fields.items():
                py_type = fmeta.annotation
                col_type = PY_TYPE_MAP.get(py_type, String)
                # assume 'id' is primary key
                if fname == meta.primary_key:
                    cols.append(Column(fname, col_type, primary_key=True))
                else:
                    cols.append(Column(fname, col_type))
            tbl = Table(table_name, self.metadata, *cols)
            self.tables[name] = tbl

    async def connect(self) -> None:
        # create tables if not exist
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)
        logger.debug("[Guaro SQL] Connected and ensured tables exist")

    async def disconnect(self) -> None:
        await self.engine.dispose()
        logger.debug("[Guaro SQL] Engine disposed")

    def _table_for(self, entity: str) -> Table:
        return self.tables[entity]

    async def execute_query(self, ir: QueryIR) -> List[Any]:
        tbl = self._table_for(ir.entity)
        cols = [tbl.c[field] for field in (ir.fields or [c.name for c in tbl.columns])]
        stmt = select(*cols)
        # filters (only == supported)
        for (field, op, value) in ir.filters:
            if op == "==":
                stmt = stmt.where(tbl.c[field] == value)
        # pagination
        if ir.pagination.get("limit") is not None:
            stmt = stmt.limit(ir.pagination.get("limit"))
        if ir.pagination.get("offset"):
            stmt = stmt.offset(ir.pagination.get("offset"))

        logger.debug(f"[Guaro SQL] Executing: {stmt}")
        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            rows = result.fetchall()

        # Map to model instances
        model_cls = self.registry.models[ir.entity].model_cls
        instances = []
        for row in rows:
            data = dict(row._mapping)
            inst = model_cls(**data)
            model_cls.bind_registry(self.registry)
            instances.append(inst)
        logger.debug(f"[Guaro SQL] Rows fetched: {len(instances)}")
        return instances

    async def insert(self, entity: str, data: Dict[str, Any]) -> Any:
        tbl = self._table_for(entity)
        stmt = sa_insert(tbl).values(**data)
        logger.debug(f"[Guaro SQL] Insert: {stmt}")
        async with self.engine.begin() as conn:
            result = await conn.execute(stmt)
            # try to fetch inserted primary key
            try:
                pk = result.inserted_primary_key[0]  # type: ignore[attr-defined]
            except Exception:
                pk = None
        if pk is not None:
            # return created instance
            model_cls = self.registry.models[entity].model_cls
            # fetch created row
            sel = select(tbl).where(tbl.c[self.registry.models[entity].primary_key] == pk)
            async with self.engine.connect() as conn:
                r = await conn.execute(sel)
                row = r.fetchone()
                data = dict(row._mapping)
            inst = model_cls(**data)
            model_cls.bind_registry(self.registry)
            return inst
        # fallback: return raw data
        return data

    async def update(self, ir: QueryIR, data: Dict[str, Any]) -> Any:
        tbl = self._table_for(ir.entity)
        stmt = sa_update(tbl).values(**data)
        for (field, op, value) in ir.filters:
            if op == "==":
                stmt = stmt.where(tbl.c[field] == value)
        logger.debug(f"[Guaro SQL] Update: {stmt}")
        async with self.engine.begin() as conn:
            result = await conn.execute(stmt)
            return result.rowcount

    async def delete(self, ir: QueryIR) -> int:
        tbl = self._table_for(ir.entity)
        stmt = sa_delete(tbl)
        for (field, op, value) in ir.filters:
            if op == "==":
                stmt = stmt.where(tbl.c[field] == value)
        logger.debug(f"[Guaro SQL] Delete: {stmt}")
        async with self.engine.begin() as conn:
            result = await conn.execute(stmt)
            return result.rowcount
