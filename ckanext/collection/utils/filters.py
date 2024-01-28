from __future__ import annotations

from typing import Any, Sequence

import sqlalchemy as sa

from ckanext.collection import shared, types


class Filters(
    types.BaseFilters,
    shared.Domain[types.TDataCollection],
):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters and action
    buttions(Download, Export, etc.).

    """

    def make_filters(self) -> Sequence[types.Filter[Any]]:
        return []

    def make_actions(self) -> Sequence[types.Filter[Any]]:
        return []

    static_filters: Sequence[types.Filter[Any]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_actions: Sequence[types.Filter[Any]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.filters = self.static_filters or self.make_filters()
        self.actions = self.static_actions or self.make_actions()


class DbFilters(Filters[types.TDbCollection]):
    pass


class TableFilters(DbFilters[types.TDbCollection]):
    table: str = shared.configurable_attribute()

    def make_filters(self) -> Sequence[types.Filter[Any]]:
        return [
            filter
            for c in self.attached.db_connection.inspector.get_columns(self.table)
            if (filter := self._filter_for(c))
        ]

    def _filter_for(self, column: dict[str, Any]) -> types.Filter[Any] | None:
        if column["name"] in self.attached.columns.filterable:
            if isinstance(column["type"], sa.Boolean):
                return self._boolean_filter(column)

            return self._input_filter(column)

        if column["name"] in self.attached.columns.searchable:
            return self._input_filter(column)

        return None

    def _filter_label(self, column: dict[str, Any]) -> str:
        return self.attached.columns.labels.get(column["name"], column["name"])

    def _boolean_filter(self, column: dict[str, Any]) -> types.Filter[Any]:
        options = [
            types.SelectOption(text="All", value=""),
            types.SelectOption(text="Yes", value="t"),
            types.SelectOption(text="No", value="f"),
        ]
        return types.SelectFilter(
            name=column["name"],
            type="select",
            options=types.SelectFilterOptions(
                label=self._filter_label(column),
                options=options,
            ),
        )

    def _distinct_filter(self, column: dict[str, Any]) -> types.Filter[Any]:
        with self.attached.db_connection.engine.connect() as conn:
            values = conn.scalars(
                sa.select(sa.distinct(sa.column(column["name"]))).select_from(
                    sa.table(self.table),
                ),
            )
        options = [types.SelectOption(text="All", value="")] + [
            types.SelectOption(text=v, value=v) for v in values
        ]
        return types.SelectFilter(
            name=column["name"],
            type="select",
            options=types.SelectFilterOptions(
                label=self._filter_label(column),
                options=options,
            ),
        )

    def _input_filter(self, column: dict[str, Any]) -> types.Filter[Any]:
        return types.InputFilter(
            name=column["name"],
            type="input",
            options=types.InputFilterOptions(
                label=self._filter_label(column),
            ),
        )
