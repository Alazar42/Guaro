from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class QuerySet(Protocol):
    async def all(self) -> list[Any]: ...

    async def get(self, **filters: Any) -> Any: ...

    async def filter(self, **filters: Any) -> list[Any]: ...


class Repository(Protocol):
    async def query(self, model_name: str) -> QuerySet: ...


class Loader(Protocol):
    async def load_many(self, keys: list[Any]) -> dict[Any, Any]: ...

    async def load_one(self, key: Any) -> Any: ...


@dataclass(slots=True)
class InMemoryQuerySet:
    rows: list[Any]

    async def all(self) -> list[Any]:
        return list(self.rows)

    async def get(self, **filters: Any) -> Any:
        for row in self.rows:
            if all(getattr(row, key, None) == value for key, value in filters.items()):
                return row
        return None

    async def filter(self, **filters: Any) -> list[Any]:
        return [row for row in self.rows if all(getattr(row, key, None) == value for key, value in filters.items())]
