from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


BatchFetch = Callable[[list[Any]], Awaitable[dict[Any, Any]] | dict[Any, Any]]


@dataclass
class BatchLoader:
    fetch: BatchFetch
    cache: dict[Any, Any] = field(default_factory=dict)

    async def load(self, key: Any) -> Any:
        if key in self.cache:
            return self.cache[key]
        result = await self.load_many([key])
        return result.get(key)

    async def load_many(self, keys: list[Any]) -> dict[Any, Any]:
        missing = [key for key in keys if key not in self.cache]
        if missing:
            outcome = self.fetch(missing)
            if hasattr(outcome, "__await__"):
                outcome = await outcome
            self.cache.update(outcome)
        return {key: self.cache.get(key) for key in keys}
