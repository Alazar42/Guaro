from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


BatchFetch = Callable[[list[Any]], Awaitable[dict[Any, Any]] | dict[Any, Any]]


@dataclass(slots=True)
class RelationLoader:
    key: str
    fetch_many: BatchFetch
    cache: dict[Any, Any] = field(default_factory=dict)

    async def load_many(self, keys: list[Any]) -> dict[Any, Any]:
        missing = [key for key in keys if key not in self.cache]
        if missing:
            result = self.fetch_many(missing)
            if hasattr(result, "__await__"):
                result = await result
            self.cache.update(result)
        return {key: self.cache.get(key) for key in keys}

    async def load_one(self, key: Any) -> Any:
        result = await self.load_many([key])
        return result.get(key)

    def clone(self) -> "RelationLoader":
        return RelationLoader(self.key, self.fetch_many)


def clone_request_loaders(loaders: dict[str, Any]) -> dict[str, Any]:
    cloned: dict[str, Any] = {}
    for name, loader in loaders.items():
        if hasattr(loader, "clone"):
            cloned[name] = loader.clone()
        else:
            cloned[name] = copy.copy(loader)
    return cloned


def loader_key(model_name: str, field_name: str) -> str:
    return f"{model_name}.{field_name}"
