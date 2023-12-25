from __future__ import annotations

from ckanext.collection import shared, types


class Filters(
    types.BaseFilters,
    shared.Domain[types.TDataCollection],
):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters and action
    buttions(Download, Export, etc.).

    """

    def make_filters(self) -> list[types.Filter]:
        return []

    def make_actions(self) -> list[types.Filter]:
        return []

    filters: list[types.Filter] = shared.configurable_attribute(
        default_factory=make_filters,
    )
    actions: list[types.Filter] = shared.configurable_attribute(
        default_factory=make_actions,
    )
