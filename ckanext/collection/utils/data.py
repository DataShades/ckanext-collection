from __future__ import annotations

import logging
from functools import cached_property
from typing import Any, Iterable, cast

import sqlalchemy as sa
from sqlalchemy.orm import Mapper
from sqlalchemy.sql import Select

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.types import Context

from ckanext.collection import shared, types

log = logging.getLogger(__name__)


class Data(
    types.BaseData,
    shared.Domain[types.TDataCollection],
):
    """Data source for collection.

    This class produces data for collection.

    Attributes:
      total: total number of available records
      data: slice of all available data.
    """

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.refresh_data()

    def refresh_data(self):
        """Pull and slice data, updating `total`.

        This operation is similar to creating a new data object with the same
        settings.

        """
        data = self.get_initial_data()

        self.total = self.compute_total(data)
        self.data = self.slice_data(data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(cast(Any, self.data))

    def get_initial_data(self) -> Any:
        """Return base data collection(with filters applied).

        Data returned from this method will be used in `compute_total` and
        `slice_data`. Return anything that allows computing total number of
        records and data slice.

        If you are using in-memory data source, return the whole collection and
        compute its lenght and slice it in corresponding methods. If you are
        working with DB, return query without limit/offset, apply `count` SQL
        function to it in `compute_total` and add limit/offset in
        `slice_data`. Finally, if you are working with API, like
        `package_search`, you can return `{"count": N, "results": ...}` from
        this method and extract fields in `compute_total`/`slice_data`.

        """
        return []

    def compute_total(self, data: Any) -> int:
        """Return total number of records."""
        return len(data)

    def slice_data(self, data: Any):
        """Return data slice according to pager settings."""
        return data[self.attached.pager.start : self.attached.pager.end]


class StaticData(Data[types.TDataCollection]):
    initial_data = shared.configurable_attribute(default_factory=lambda self: [])

    def get_initial_data(self) -> Any:
        return self.initial_data


class ModelData(Data[types.TDataCollection]):
    """DB data source.

    This base class is suitable for building SQL query.

    Attributes:
      model: main model used by data source
    """

    model: Any = shared.configurable_attribute(None)
    is_scalar: bool = shared.configurable_attribute(False)
    static_columns: list[sa.Column[Any]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_filters: list[Any] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_sources: dict[str, Any] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )
    static_joins: list[tuple[str, Any, bool]] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )

    def get_initial_data(self):
        """@inherit"""
        stmt = self.get_base_statement()
        stmt = self.alter_statement(stmt)
        stmt = self.statement_with_filters(stmt)
        return self.statement_with_sorting(stmt)

    def compute_total(self, data: Select) -> int:
        """@inherit"""
        return self.count_statement(data)

    def slice_data(self, data: Select) -> Iterable[Any]:
        """@inherit"""
        stmt = self.statement_with_limits(data)

        if self.is_scalar:
            return model.Session.scalars(stmt).all()

        return model.Session.execute(stmt).all()

    def select_columns(self) -> Iterable[Any]:
        """Return list of columns for select statement."""
        if self.static_columns:
            return self.static_columns

        if not self.model:
            return []

        mapper = cast(Mapper, sa.inspect(self.model))
        return [self.model] if self.is_scalar else [mapper.columns]

    def get_extra_sources(self) -> dict[str, Any]:
        """Return mapping of additional models/subqueries used to build the
        statement.

        Note: Don't call this method direclty. Instead, use `extra_sources`
        property, that caches return value of the current method. Extra sources
        must not change during query building process.

        Extra sources are used when the query contains subqueries or joins with
        aliased models. For example, in order to select column from joined
        subquery, instead of creating identical subqueries inside
        `select_columns` and `get_joins`, write the following code:

        >>> def get_extra_sources(self):
        >>>     return {"subq": make_subquery()}
        >>>
        >>> def select_columns(self):
        >>>     return [self.extra_sources["subq"].c.column_name]
        >>>
        >>> def get_joins(self):
        >>>     subq = self.extra_sources["subq"]
        >>>     return [("subq", subq.c.id == self.model.id, False)]

        """
        return self.static_sources

    @cached_property
    def extra_sources(self) -> dict[str, Any]:
        """Cache for extra sources.

        If you are going to override this property, don't forget to add
        `cached_property` decorator. The better option would be to override
        `get_extra_sources`. In this way you will not be affected if cache
        implementation changes in future.
        """
        return self.get_extra_sources()

    def get_joins(self) -> Iterable[tuple[str, Any, bool]]:
        """Return join details for extra_sources.

        Every item is a tuple of of (extra_source_name, join_condition,
        outerjoin_flag)
        """
        return self.static_joins

    def apply_joins(self, stmt: Select) -> Select:
        """Return list of columns for select statement."""

        sources = self.extra_sources

        for name, condition, isouter in self.get_joins():
            stmt = stmt.join(sources[name], condition, isouter)

        return stmt

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        columns = self.select_columns()
        stmt = sa.select(*columns)
        if self.model:
            stmt = stmt.select_from(self.model)

        return self.apply_joins(stmt)

    def alter_statement(self, stmt: Select):
        """Add columns, joins and unconditional filters to statement."""
        return stmt

    def count_statement(self, stmt: Select) -> int:
        """Count number of items in query"""
        return cast(
            int,
            model.Session.execute(
                sa.select(sa.func.count()).select_from(stmt),
            ).scalar(),
        )

    def statement_with_filters(self, stmt: Select):
        """Add normal filter to statement."""
        for cond in self.static_filters:
            stmt = stmt.where(cond)

        return stmt

    def statement_with_sorting(self, stmt: Select):
        """Specify sorting order for statement."""
        sort = self.attached.params.get("sort")
        if not sort:
            return stmt

        desc = False
        if sort.startswith("-"):
            sort = sort[1:]
            desc = True

        elif len(parts := sort.split()) == 2:
            sort, direction = parts

            if direction.lower() == "desc":
                desc = True

        if sort not in self.attached.columns.sortable and sort not in stmt.columns:
            log.warning("Unexpected sort value: %s", sort)
            return stmt

        if desc:
            sort = f"{sort} DESC"

        return stmt.order_by(sa.text(sort))

    def statement_with_limits(self, stmt: Select):
        limit = self.attached.pager.size
        offset = self.attached.pager.start

        return stmt.limit(limit).offset(offset)


class ApiData(Data[types.TDataCollection]):
    """API data source.

    This base class is suitable for building API calls.

    Attributes:
      action: API action that returns the data
    """

    action: str = shared.configurable_attribute(None)
    payload: dict[str, Any] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )

    def make_context(self):
        return Context()

    def make_payload(self) -> dict[str, Any]:
        return dict(
            self.payload or {},
            **self.get_filters(),
            **self.get_offsets(),
            **self.get_sort(),
        )

    def get_offsets(self) -> dict[str, Any]:
        return {
            "start": self.attached.pager.start,
            "rows": self.attached.pager.size,
        }

    def get_filters(self) -> dict[str, str]:
        return {}

    def get_sort(self) -> dict[str, str]:
        sort = self.attached.params.get("sort")
        if not sort:
            return {}

        direction = "asc"
        if sort.startswith("-"):
            sort = sort[1:]
            direction = "desc"

        if sort not in self.attached.columns.sortable:
            log.warning("Unexpected sort value: %s", sort)
            return {}

        return {"sort": f"{sort} {direction}"}

    def get_initial_data(self):
        action = tk.get_action(self.action)
        return action(self.make_context(), self.make_payload())

    def compute_total(self, data: dict[str, Any]) -> int:
        return data["count"]

    def slice_data(self, data: dict[str, Any]):
        return data["results"]
