from __future__ import annotations

import abc
from typing import Any, Callable, Generic

from typing_extensions import Self

from ckanext.collection.types import TDataCollection


class AttachTrait(abc.ABC, Generic[TDataCollection]):
    """Attach collection to the current object"""

    __collection: TDataCollection

    def attach(self, obj: TDataCollection):
        self.__collection = obj

    @property
    def attached(self) -> TDataCollection:
        return self.__collection


class AttrSettingsTrait(abc.ABC):
    _attr_settings: dict[str, Callable[[Self], Any] | None] = {}

    def gather_settings(self, kwargs: dict[str, Any]):
        for k, default_factory in self._attr_settings.items():
            if k in kwargs:
                setattr(self, k, kwargs.pop(k))

            elif default_factory:
                setattr(self, k, default_factory(self))
