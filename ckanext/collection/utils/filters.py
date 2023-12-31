from __future__ import annotations

from typing import Any

from ckanext.collection import shared, types


class Filters(
    types.BaseFilters,
    shared.Domain[types.TDataCollection],
):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters and action
    buttions(Download, Export, etc.).

    """

    def make_filters(self) -> list[types.Filter[Any]]:
        return []

    def make_actions(self) -> list[types.Filter[Any]]:
        return []

    static_filters: list[types.Filter[Any]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_actions: list[types.Filter[Any]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.filters = self.static_filters or self.make_filters()
        self.actions = self.static_actions or self.make_actions()
