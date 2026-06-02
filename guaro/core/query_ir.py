from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RelationSelection:
    fields: List[str] = field(default_factory=list)
    relations: Dict[str, "RelationSelection"] = field(default_factory=dict)


@dataclass
class QueryIR:
    """Database-agnostic Query Intermediate Representation.

    - entity: logical model name (e.g., "User")
    - fields: list of top-level fields to select
    - relations: nested relation selections
    - filters: list of simple filter tuples (field, op, value)
    - pagination: dict with limit/offset or page/size
    - sort: list of (field, direction)
    """

    entity: str
    fields: List[str] = field(default_factory=list)
    relations: Dict[str, RelationSelection] = field(default_factory=dict)
    filters: List[tuple[str, str, Any]] = field(default_factory=list)
    pagination: Dict[str, Any] = field(default_factory=dict)
    sort: List[tuple[str, str]] = field(default_factory=list)

    def add_filter(self, field: str, op: str, value: Any) -> None:
        self.filters.append((field, op, value))

    def set_pagination(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> None:
        if limit is not None:
            self.pagination["limit"] = limit
        if offset is not None:
            self.pagination["offset"] = offset
 