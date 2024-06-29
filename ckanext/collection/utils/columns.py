from __future__ import annotations

import enum
from typing import Any, cast

from ckanext.collection import shared, types


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

    class Default(shared.Sentinel, enum.Enum):
        ALL = enum.auto()
        NOT_HIDDEN = enum.auto()
        NONE = enum.auto()

    names: list[str] = shared.configurable_attribute(default_factory=lambda self: [])
    hidden: set[str] = shared.configurable_attribute(default_factory=lambda self: set())
    visible: set[str] = shared.configurable_attribute(Default.NOT_HIDDEN)
    sortable: set[str] = shared.configurable_attribute(Default.ALL)
    filterable: set[str] = shared.configurable_attribute(Default.ALL)
    searchable: set[str] = shared.configurable_attribute(Default.NONE)
    labels: dict[str, str] = shared.configurable_attribute(Default.ALL)

    serializers: dict[
        str,
        list[tuple[str, dict[str, Any]]],
    ] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )

    def __init__(self, obj: types.TDataCollection, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.configure_attributes()

    def configure_attributes(self):
        if self.hidden is self.Default.ALL:
            self.hidden = set(self.names)
        elif isinstance(self.hidden, self.Default):
            self.hidden = set()

        self.visible = self._compute_set(self.visible)

        if not self.hidden:
            self.hidden = set(self.names) - self.visible

        self.sortable = self._compute_set(self.sortable)
        self.filterable = self._compute_set(self.filterable)
        self.searchable = self._compute_set(self.searchable)

        if isinstance(self.labels, self.Default):
            self.labels = {c: c for c in self._compute_set(self.labels)}

    def _compute_set(self, value: Default | set[str]):
        if value is self.Default.NONE:
            return cast("set[str]", set())

        if value is self.Default.ALL:
            return {c for c in self.names}

        if value is self.Default.NOT_HIDDEN:
            return {c for c in self.names if c not in self.hidden}

        return value

    def get_primary_order(self, name: str) -> str:
        """Format column name for usage as a primary order value.

        Args:
          name: the name of sorted column
        """
        return name

    def get_secondary_order(self, name: str) -> str:
        """Format column name for usage as a secondary order value."""
        return f"-{name}"


class DbColumns(Columns[types.TDbCollection]):
    pass


class TableColumns(DbColumns[types.TDbCollection]):
    table: str = shared.configurable_attribute()
    filterable: set[str] = shared.configurable_attribute(
        default_factory=lambda self: self.Default.NONE,
    )

    def configure_attributes(self):
        self.names = [
            c["name"]
            for c in self.attached.db_connection.inspector.get_columns(self.table)
        ]
        super().configure_attributes()
