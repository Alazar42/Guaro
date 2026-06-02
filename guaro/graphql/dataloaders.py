from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from guaro.batching.loader import BatchLoader


@dataclass
class LoaderRegistry:
    loaders: dict[str, BatchLoader] = field(default_factory=dict)

    def get(self, name: str, loader_factory: Any) -> BatchLoader:
        if name not in self.loaders:
            self.loaders[name] = loader_factory()
        return self.loaders[name]
