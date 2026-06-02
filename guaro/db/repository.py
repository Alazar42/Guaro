from __future__ import annotations

from typing import Any

from guaro.core.query_ir import QueryIR
from guaro.db.adapters.base import DatabaseAdapter


class Repository:
    """Repository interface that operates on QueryIR and delegates to an adapter."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self.adapter = adapter

    async def find(self, ir: QueryIR) -> Any:
        return await self.adapter.execute_query(ir)

    async def create(self, entity: str, data: dict[str, Any]) -> Any:
        return await self.adapter.insert(entity, data)

    async def update(self, ir: QueryIR, data: dict[str, Any]) -> Any:
        return await self.adapter.update(ir, data)

    async def delete(self, ir: QueryIR) -> Any:
        return await self.adapter.delete(ir)
