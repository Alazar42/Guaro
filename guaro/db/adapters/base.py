from __future__ import annotations

from typing import Any

from guaro.core.query_ir import QueryIR


class DatabaseAdapter:
    """Base interface for database adapters."""

    async def execute_query(self, ir: QueryIR) -> Any:
        raise NotImplementedError()

    async def insert(self, entity: str, data: dict[str, Any]) -> Any:
        raise NotImplementedError()

    async def update(self, ir: QueryIR, data: dict[str, Any]) -> Any:
        raise NotImplementedError()

    async def delete(self, ir: QueryIR) -> Any:
        raise NotImplementedError()
