from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

from guaro.core.registry import Registry, RouteMetadata
from guaro.dependency.injector import DependencyInjector
from guaro.execution.context import ExecutionContext
from guaro.execution.pipeline import ExecutionPipeline
from guaro.execution.planner import QueryPlan, build_query_plan
from guaro.core.query_ir import QueryIR, RelationSelection
from guaro.db.repository import Repository
from guaro.db.router import get_adapter


@dataclass(slots=True)
class ExecutionResult:
    data: Any
    plan: QueryPlan | None = None


@dataclass
class ExecutionEngine:
    registry: Registry
    cache: dict[str, Any] = field(default_factory=dict)
    injector: DependencyInjector = field(init=False)
    pipeline: ExecutionPipeline = field(init=False)

    def __post_init__(self) -> None:
        self.injector = DependencyInjector(self.registry)
        self.pipeline = ExecutionPipeline(self.registry.middleware)

    async def execute(self, route: RouteMetadata, *, context: ExecutionContext, kwargs: dict[str, Any] | None = None) -> ExecutionResult:
        kwargs = kwargs or {}
        context.route = route
        context.operation = route.name
        context.selected_fields = context.selected_fields or set()
        pipeline = ExecutionPipeline(self.registry.middleware + route.middleware)

        model_metadata = self.registry.models.get(route.model_name or "") if route.model_name else None
        plan = build_query_plan(route.model_name or route.name, context.selected_fields, transport=context.transport)
        context.plan = plan
        if not context.field_tree:
            context.field_tree = plan.field_tree

        try:
            await pipeline.before(context)
            self._enforce_permissions(route, context)
            self._enforce_auth(route, context)

            # If this route targets a model and is a GET, use Repository + QueryIR
            if model_metadata is not None and route.method == "GET":
                # build QueryIR from selection and params
                ir = QueryIR(entity=model_metadata.name)
                # fields - exclude relations (they are not stored as db columns)
                if context.selected_fields:
                    ir.fields = list(context.selected_fields)
                else:
                    # Include only scalar fields, exclude relations
                    ir.fields = [
                        fname
                        for fname, fmeta in model_metadata.fields.items()
                        if not fmeta.relationship
                    ]

                # relations from context.field_tree
                def build_relations(tree: dict[str, Any]) -> dict[str, RelationSelection]:
                    rels: dict[str, RelationSelection] = {}
                    for k, v in tree.items():
                        sel = RelationSelection()
                        sel.fields = list(v.get("fields", []))
                        sel.relations = build_relations(v.get("relations", {}))
                        rels[k] = sel
                    return rels

                ir.relations = build_relations(context.field_tree or {})

                # params -> filters (support primary key lookup if id provided)
                primary = model_metadata.primary_key
                if primary in kwargs:
                    ir.add_filter(primary, "==", kwargs[primary])
                    ir.set_pagination(limit=1, offset=0)

                # select cached adapter from database router
                adapter = get_adapter(self.registry)

                repo = Repository(adapter)
                outcome = await repo.find(ir)
                # if single item requested, return single object
                if ir.pagination.get("limit") == 1:
                    outcome = outcome[0] if outcome else None

                # serialize outcome if model metadata present
                if model_metadata is not None:
                    outcome = await self._serialize_result(outcome, model_metadata, context, plan)

                await pipeline.after(context, outcome)
                return ExecutionResult(data=outcome, plan=plan)

            # default path: call resolver as before
            resolved_kwargs = await self.injector.resolve(route.resolver, context, kwargs)
            outcome = route.resolver(**resolved_kwargs)
            if inspect.isawaitable(outcome):
                outcome = await outcome
            if model_metadata is not None:
                outcome = await self._serialize_result(outcome, model_metadata, context, plan)
            await pipeline.after(context, outcome)
            return ExecutionResult(data=outcome, plan=plan)
        except Exception as exc:
            context.errors.append(exc)
            await pipeline.on_error(context, exc)
            raise

    def _enforce_auth(self, route: RouteMetadata, context: ExecutionContext) -> None:
        if getattr(route.resolver, "__guaro_requires_auth__", False) and context.user is None:
            raise PermissionError(f"Authentication required for {route.method} {route.path}")

    def _enforce_permissions(self, route: RouteMetadata, context: ExecutionContext) -> None:
        missing = [permission_name for permission_name in route.permissions if permission_name not in context.permissions]
        if missing:
            raise PermissionError(f"Permission '{missing[0]}' required for {route.method} {route.path}")

    async def _serialize_result(self, result: Any, model_metadata: Any, context: ExecutionContext, plan: QueryPlan) -> Any:
        serializer = self.registry.compiled_serializers.get(model_metadata.name)
        if serializer is None:
            from guaro.serialization.compiler import compile_serializer

            serializer = compile_serializer(self.registry, model_metadata)

        if isinstance(result, list):
            return await serializer.serialize(result, context, plan, context.field_tree)
        if hasattr(result, "__guaro_model__") or result.__class__.__name__ in self.registry.models:
            return await serializer.serialize(result, context, plan, context.field_tree)
        return result
