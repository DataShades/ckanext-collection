from __future__ import annotations

from typing import Any

from ckanext.collection import types

from .shared import AttachTrait, AttrSettingsTrait


class Filters(
    types.BaseFilters[types.TDataCollection],
    AttachTrait[types.TDataCollection],
    AttrSettingsTrait,
):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters and action
    buttions(Download, Export, etc.).

    """

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        self._attach(obj)
        self._gather_settings(kwargs)

        self.dropdowns = kwargs.get("filters", self.make_filters())
        self.actions = kwargs.get("actions", self.make_actions())

    def make_filters(self) -> list[types.Filter]:
        return []

    def make_actions(self) -> list[types.Filter]:
        return []
