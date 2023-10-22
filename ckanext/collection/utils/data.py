from __future__ import annotations
import copy
import logging
import ckan.plugins.toolkit as tk
from ckan import types
from typing import Any, Iterable, cast
from ckan import model
import sqlalchemy as sa
from functools import cached_property
from ckanext.collection.types import TDataCollection
from .shared import AttachTrait

log = logging.getLogger(__name__)


class Data(AttachTrait[TDataCollection]):
    """Data source for collection.

    This class produces data for collection.

    Attributes:
      total: total number of available records
      data: slice of all available data.
    """

    total: int = 0
    data: Iterable[Any]

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        self.attach(obj)

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
        return [
            {"field": "hello", "value": "Hello"},
            {"field": "world", "value": "World"},
        ]

    def compute_total(self, data: Any) -> int:
        """Return total number of records."""
        return len(data)

    def slice_data(self, data: Any):
        """Return data slice according to pager settings."""
        return data


class ModelData(Data[TDataCollection]):
    """DB data source.

    This base class is suitable for building SQL query.

    Attributes:
      model: main model used by data source
    """

    model: Any = None

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        """Set model before data is computed"""
        if model := kwargs.get("model"):
            self.model = model

        super().__init__(obj, **kwargs)

    def select_columns(self) -> Iterable[Any]:
        """Return list of columns for select statement."""
        return sa.inspect(self.model).columns if self.model else []

    @cached_property
    def extra_sources(self) -> dict[str, Any]:
        """Return mapping of additional models/subqueries used to build the
        statement.

        Result is cached after first invocation because sources must not change
        during query building process.

        """
        return {}

    def get_joins(self) -> Iterable[tuple[str, Any, bool]]:
        """Return join details for extra_sources.

        Every item is a tuple of of (extra_source_name, join_condition,
        outerjoin_flag)
        """
        return []

    def apply_joins(self, stmt: sa.select) -> sa.select:
        """Return list of columns for select statement."""

        sources = self.extra_sources

        for name, condition, isouter in self.get_joins():
            stmt = cast(sa.select, stmt.join(sources[name], condition, isouter))

        return stmt

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        columns = self.select_columns()
        stmt = sa.select(*columns)
        if self.model:
            stmt = stmt.select_from(self.model)

        return self.apply_joins(stmt)

    def alter_statement(self, stmt: sa.select):
        """Add columns, joins and unconditional filters to statement."""
        return stmt

    def count_statement(self, stmt: sa.select) -> int:
        """Count number of items in query"""
        return cast(
            int,
            model.Session.execute(
                sa.select(sa.func.count()).select_from(stmt),
            ).scalar(),
        )

    def statement_with_filters(self, stmt: sa.select):
        return stmt

    def statement_with_sorting(self, stmt: sa.select):
        sort = self._collection.params.get("sort")
        if not sort:
            return stmt

        desc = False
        if sort.startswith("-"):
            sort = sort[1:]
            desc = True

        if sort not in self._collection.columns.sortable:
            log.warning("Unexpected sort value: %s", sort)
            return stmt

        if desc:
            sort = f"{sort} DESC"

        return stmt.order_by(sa.text(sort))

    def statement_with_limits(self, stmt: sa.select):
        limit = self._collection.pager.size
        offset = self._collection.pager.start

        return stmt.limit(limit).offset(offset)

    def get_initial_data(self):
        stmt = self.get_base_statement()
        stmt = self.alter_statement(stmt)
        stmt = self.statement_with_filters(stmt)
        stmt = self.statement_with_sorting(stmt)

        return stmt

    def compute_total(self, data: sa.select) -> int:
        return self.count_statement(data)

    def slice_data(self, data: sa.select):
        stmt = self.statement_with_limits(data)

        rows: Any = model.Session.execute(stmt)
        return [dict(zip(row.keys(), row)) for row in rows]


class ApiData(Data[TDataCollection]):
    """API data source.

    This base class is suitable for building API calls.

    Attributes:
      action: API action that returns the data
    """

    action: str
    payload: dict[str, Any] | None = None

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        """Set model before data is computed"""
        if action := kwargs.get("action"):
            self.action = action

        payload = kwargs.get("payload")
        if payload is not None:
            self.payload = payload

        super().__init__(obj, **kwargs)

    def make_context(self):
        return types.Context()

    def make_payload(self) -> dict[str, Any]:

        return dict(
            self.payload or {},
            **self.get_filters(),
            **self.get_offsets(),
            **self.get_sort(),
        )

    def get_offsets(self) -> dict[str, Any]:
        return {
            "start": self._collection.pager.start,
            "rows": self._collection.pager.size,
        }

    def get_filters(self) -> dict[str, str]:
        return {}

    def get_sort(self) -> dict[str, str]:
        sort = self._collection.params.get("sort")
        if not sort:
            return {}

        direction = "asc"
        if sort.startswith("-"):
            sort = sort[1:]
            direction = "desc"

        if sort not in self._collection.columns.sortable:
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
