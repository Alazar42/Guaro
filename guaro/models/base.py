from __future__ import annotations

from typing import Any, ClassVar

from guaro.core.registry import Registry


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
    def all(cls) -> list[Model]:
        store = cls._registry().serializers.setdefault(f"store:{cls.__name__}", [])
        return list(store)

    @classmethod
    def find(cls, identifier: Any) -> Model | None:
        metadata = cls._metadata()
        primary_key = metadata.primary_key
        for item in cls.all():
            if getattr(item, primary_key, None) == identifier:
                return item
        return None

    @classmethod
    def save(cls, instance: Model) -> Model:
        store = cls._registry().serializers.setdefault(f"store:{cls.__name__}", [])
        store.append(instance)
        return instance
