from __future__ import annotations

import abc
from collections.abc import Iterable, Sized
from typing import Any, Generic, TypedDict, TypeVar

from typing_extensions import Self

from ckanext.collection import types

TDataCollection = TypeVar("TDataCollection", bound="BaseCollection")


class BaseColumns(abc.ABC, Generic[types.TDataCollection]):
    """Declaration of columns properties"""

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]


class BaseData(abc.ABC, Generic[types.TDataCollection], Sized, Iterable[Any]):
    """Declaration of data properties."""

    total: int = 0
    data: Iterable[Any]


class BaseFilters(abc.ABC, Generic[types.TDataCollection]):
    """Declaration of filters properties."""

    dropdowns: list[types.Filter]
    date_range: types.DateRange | None
    actions: list[Any]


class BasePager(abc.ABC, Generic[types.TDataCollection]):
    """Declaration of pager properties"""

    params: dict[str, Any]
    start: Any
    end: Any
    size: Any


class BaseSerializer(abc.ABC, Generic[types.TDataCollection]):
    pass


class BaseCollection(abc.ABC):
    """Declaration of collection properties."""

    name: str
    params: dict[str, Any]

    columns: BaseColumns[Self]
    data: BaseData[Self]
    filters: BaseFilters[Self]
    pager: BasePager[Self]
    serializer: BaseSerializer[Self]


class Option(TypedDict):
    """Single option for Filter."""

    value: str
    label: str


class Filter(TypedDict):
    """Dropdown filter."""

    name: str
    placeholder: str | None
    options: list[Option]


class DateRange(TypedDict):
    """After/before datepicker."""

    name: str
    label: str
