from __future__ import annotations

from typing import Any, ClassVar

from guaro.core.registry import Registry
from guaro.db.router import get_adapter


class Model:
    __guaro_registry__: ClassVar[Registry | None] = None

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def bind_registry(cls, registry: Registry) -> None:
        cls.__guaro_registry__ = registry

    @classmethod
    def _registry(cls) -> Registry:
        if cls.__guaro_registry__ is None:
            raise RuntimeError(f"{cls.__name__} is not bound to a Guaro registry")
        return cls.__guaro_registry__

    @classmethod
    def _metadata(cls):
        return cls._registry().get_model_metadata(cls)
    @classmethod
    async def all(cls) -> list[Model]:
        registry = cls._registry()
        adapter = get_adapter(registry)
        # Repository and QueryIR are used for all adapters
        from guaro.db.repository import Repository
        from guaro.core.query_ir import QueryIR

        repo = Repository(adapter)
        ir = QueryIR(entity=cls._metadata().name)
        rows = await repo.find(ir)
        return cls._rows_to_models(rows)

    @classmethod
    async def find(cls, identifier: Any) -> Model | None:
        registry = cls._registry()
        metadata = cls._metadata()
        primary_key = metadata.primary_key
        adapter = get_adapter(registry)
        from guaro.db.repository import Repository
        from guaro.core.query_ir import QueryIR

        repo = Repository(adapter)
        ir = QueryIR(entity=metadata.name)
        ir.add_filter(primary_key, "==", identifier)
        ir.set_pagination(limit=1, offset=0)
        rows = await repo.find(ir)
        if not rows:
            return None
        models = cls._rows_to_models(rows)
        return models[0] if models else None

    @classmethod
    async def create(cls, **data: Any) -> Model:
        registry = cls._registry()
        adapter = get_adapter(registry)
        from guaro.db.repository import Repository

        repo = Repository(adapter)
        created = await repo.create(cls._metadata().name, data)
        if hasattr(created, "__dict__") and created.__class__ is not cls:
            try:
                created.bind_registry(registry)
            except Exception:
                pass
            return created
        if isinstance(created, dict):
            inst = cls(**created)
            inst.bind_registry(registry)
            return inst
        inst = cls(**data)
        inst.bind_registry(registry)
        return inst

    @classmethod
    async def save(cls, instance: Model) -> Model:
        registry = cls._registry()
        metadata = cls._metadata()
        primary = metadata.primary_key
        val = getattr(instance, primary, None)
        adapter = get_adapter(registry)
        from guaro.db.repository import Repository
        from guaro.core.query_ir import QueryIR

        repo = Repository(adapter)
        data = {f: getattr(instance, f, None) for f in metadata.fields.keys()}
        if val is None:
            created = await repo.create(metadata.name, data)
            if hasattr(created, "__dict__"):
                try:
                    created.bind_registry(registry)
                except Exception:
                    pass
                return created
            if isinstance(created, dict):
                inst = cls(**created)
                inst.bind_registry(registry)
                return inst
            return instance

        ir = QueryIR(entity=metadata.name)
        ir.add_filter(primary, "==", val)
        updated = await repo.update(ir, data)
        if hasattr(updated, "__dict__"):
            try:
                updated.bind_registry(registry)
            except Exception:
                pass
            return updated
        return instance

    # Provide a descriptor so `Model.delete` works both as classmethod and instance method:
    class _DeleteDescriptor:
        def __get__(self, obj, objtype=None):
            async def _instance_delete():
                inst = obj
                cls = inst.__class__
                registry = cls._registry()
                metadata = cls._metadata()
                pk = getattr(inst, metadata.primary_key, None)
                if pk is None:
                    return 0
                adapter = get_adapter(registry)
                from guaro.db.repository import Repository
                from guaro.core.query_ir import QueryIR

                repo = Repository(adapter)
                ir = QueryIR(entity=metadata.name)
                ir.add_filter(metadata.primary_key, "==", pk)
                return await repo.delete(ir)

            async def _class_delete(identifier: Any | None = None):
                if identifier is None:
                    raise ValueError("identifier required for class-level delete")
                cls = objtype
                registry = cls._registry()
                metadata = cls._metadata()
                adapter = get_adapter(registry)
                from guaro.db.repository import Repository
                from guaro.core.query_ir import QueryIR

                repo = Repository(adapter)
                ir = QueryIR(entity=metadata.name)
                ir.add_filter(metadata.primary_key, "==", identifier)
                return await repo.delete(ir)

            return _instance_delete if obj is not None else _class_delete

    delete = _DeleteDescriptor()

    @classmethod
    def _rows_to_models(cls, rows: list[Any]) -> list[Model]:
        models: list[Model] = []
        for r in rows:
            if r is None:
                continue
            # Already an instance of the target model
            if hasattr(r, "__dict__") and r.__class__ is cls:
                models.append(r)
                continue
            # If adapter returned a dict/Mapping, instantiate the model
            if isinstance(r, dict):
                inst = cls(**r)
                try:
                    inst.bind_registry(cls.__guaro_registry__)
                except Exception:
                    pass
                models.append(inst)
                continue
            # Fallback: try to turn into model via __dict__
            if hasattr(r, "__dict__"):
                inst = cls(**r.__dict__)
                try:
                    inst.bind_registry(cls.__guaro_registry__)
                except Exception:
                    pass
                models.append(inst)
                continue
        return models
