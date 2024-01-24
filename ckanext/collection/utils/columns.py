from __future__ import annotations

from typing import Any

from ckanext.collection import shared, types

SENTINEL = object()


class Columns(
    types.BaseColumns,
    shared.Domain[types.TDataCollection],
):
    """Collection of columns details for filtering/rendering.

    Attributes:
      names: list of all available columns
      visible: columns that can be viewed
      sortable: columns that can be sorted
      labels: UI labels for columns
    """

    names: list[str] = shared.configurable_attribute(default_factory=lambda self: [])
    hidden: set[str] = shared.configurable_attribute(default_factory=lambda self: set())
    visible: set[str] = shared.configurable_attribute(SENTINEL)
    sortable: set[str] = shared.configurable_attribute(SENTINEL)
    filterable: set[str] = shared.configurable_attribute(SENTINEL)
    searchable: set[str] = shared.configurable_attribute(
        default_factory=lambda self: set(),
    )
    labels: dict[str, str] = shared.configurable_attribute(SENTINEL)

    serializers: dict[
        str,
        list[tuple[str, dict[str, Any]]],
    ] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )

    def __init__(self, obj: types.TDataCollection, **kwargs: Any):
        super().__init__(obj, **kwargs)

        if self.visible is SENTINEL:
            self.visible = {c for c in self.names if c not in self.hidden}

        if self.sortable is SENTINEL:
            self.sortable = set(self.names)

        if self.filterable is SENTINEL:
            self.filterable = set(self.names)

        if self.labels is SENTINEL:
            self.labels = {c: c for c in self.names}

    def get_primary_order(self, name: str) -> str:
        """Format column name for usage as a primary order value."""
        return name

    def get_secondary_order(self, name: str) -> str:
        """Format column name for usage as a secondary order value."""
        return f"-{name}"
