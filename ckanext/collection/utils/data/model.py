from __future__ import annotations

import abc
import logging
from functools import cached_property
from typing import Any, Generic, Iterable, Iterator, TypeVar, cast

import sqlalchemy as sa
from sqlalchemy.orm import Mapper
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.selectable import GenerativeSelect, Select

from ckan import model
from ckan.types import AlchemySession

from ckanext.collection import shared, types

from .base import Data

log = logging.getLogger(__name__)
TStatement = TypeVar("TStatement", bound=GenerativeSelect)


class BaseSaData(
    Data[types.TData, types.TDataCollection],
    Generic[TStatement, types.TData, types.TDataCollection],
):
    """Data source for custom SQL statement."""

    _data: cached_property[TStatement]
    use_naive_filters: bool = shared.configurable_attribute(False)
    use_naive_search: bool = shared.configurable_attribute(False)
    session: AlchemySession = shared.configurable_attribute(
        default_factory=lambda self: model.Session,
    )

    def compute_data(self):
        stmt = self.get_base_statement()
        stmt = self.alter_statement(stmt)
        stmt = self.statement_with_filters(stmt)
        return self.statement_with_sorting(stmt)

    @abc.abstractmethod
    def get_base_statement(self) -> Any:
        """Return statement with minimal amount of columns and filters."""
        ...

    def compute_total(self, data: TStatement) -> int:
        return self.count_statement(data)

    def __iter__(self) -> Iterator[types.TData]:
        yield from self.execute_statement(self._data)

    def _execute(self, stmt: GenerativeSelect):
        return self.session.execute(stmt)

    def range(self, start: int, end: int) -> Iterable[types.TData]:
        stmt = self._data.limit(end - start).offset(start)
        return self.execute_statement(stmt)

    def execute_statement(self, stmt: TStatement) -> Iterable[types.TData]:
        result: Any = self._execute(stmt)
        return result

    def alter_statement(self, stmt: TStatement):
        """Add columns, joins and unconditional filters to statement."""
        return stmt

    def count_statement(self, stmt: TStatement) -> int:
        """Count number of items in query"""
        count_stmt: Select = sa.select(sa.func.count()).select_from(stmt)
        return cast(int, self._execute(count_stmt).scalar())

    def statement_with_filters(self, stmt: TStatement) -> TStatement:
        """Add normal filter to statement."""
        if not isinstance(stmt, Select):
            return stmt

        params = self.attached.params
        if self.use_naive_filters:
            stmt = stmt.where(
                sa.and_(
                    sa.true(),
                    *[
                        stmt.selected_columns[name] == params[name]
                        for name in self.attached.columns.filterable
                        if name in params
                        and params[name] != ""
                        and name in stmt.selected_columns
                    ],
                ),
            )

        if self.use_naive_search and (q := params.get("q")):
            stmt = stmt.where(
                sa.or_(
                    sa.false(),
                    *[
                        stmt.selected_columns[name].ilike(f"%{q}%")
                        for name in self.attached.columns.searchable
                        if name in stmt.selected_columns
                    ],
                ),
            )

        return stmt

    def statement_with_sorting(self, stmt: TStatement):
        """Specify sorting order for statement."""
        sort = self.attached.params.get("sort")
        if not sort:
            return stmt

        column, desc = shared.parse_sort(sort)

        if (
            column not in self.attached.columns.sortable
            and column not in stmt.selected_columns
        ):
            log.warning("Unexpected sort value: %s", column)
            return stmt

        sort = column
        if desc:
            sort = f"{sort} DESC"

        return stmt.order_by(sa.text(sort))


class StatementSaData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """Data source for custom SQL statement."""

    statement: Any = shared.configurable_attribute(None)

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        return self.statement


class UnionSaData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """Data source for custom SQL statement."""

    statements: Iterable[GenerativeSelect] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        return sa.select(sa.union_all(*self.statements).subquery())


class ModelData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """DB data source.

    This base class is suitable for building SQL query.

    Attributes:
      model: main model used by data source
      is_scalar: return model instance instead of columns set.
    """

    model: Any = shared.configurable_attribute(None)
    is_scalar: bool = shared.configurable_attribute(False)

    static_columns: list[sa.Column[Any] | Label[Any]] = shared.configurable_attribute(
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

    def execute_statement(self, stmt: Select) -> Iterable[types.TData]:
        result: Any
        if self.is_scalar:
            result = self.session.scalars(stmt)

        else:
            result = self.session.execute(stmt)

        return result

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

    def statement_with_filters(self, stmt: Select):
        """Add normal filter to statement."""
        for cond in self.static_filters:
            stmt = stmt.where(cond)

        return super().statement_with_filters(stmt)
