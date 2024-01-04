from __future__ import annotations

import abc
from collections.abc import Sized
from typing import Any, Callable, Generic, Iterable

from typing_extensions import TypeAlias, TypedDict, TypeVar

CollectionFactory: TypeAlias = "Callable[[str, dict[str, Any]], BaseCollection[Any]]"
TDataCollection = TypeVar("TDataCollection", bound="BaseCollection[Any]")
TFilterOptions = TypeVar("TFilterOptions")
TData = TypeVar("TData")


class BaseColumns(abc.ABC):
    """Declaration of columns properties"""

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]


class BaseData(abc.ABC, Sized, Iterable[TData]):
    """Declaration of data properties."""

    @abc.abstractproperty
    def total(self) -> int:
        """Total number of data records."""
        ...

    @abc.abstractmethod
    def range(self, start: Any, end: Any) -> Iterable[TData]:
        """Slice data using specified limits."""
        ...


class BasePager(abc.ABC):
    """Declaration of pager properties"""

    params: dict[str, Any]

    @property
    def size(self) -> Any:
        """Range of the pager.

        In classic pager it may be the number of items per page. For date range
        pager, it can be a timespan within which we are searching for records.

        """
        return self.start - self.end

    @abc.abstractproperty
    def start(self) -> Any:
        """Inclusive lower bound of the page.

        For classic limit/offset pagination, start:0 means that index of the
        first element is 0.

        """
        ...

    @abc.abstractproperty
    def end(self) -> Any:
        """Exclusive upper bound of the page.

        For classic limit/offset pagination, end:10 means that index of the
        last element is less than 10.

        """
        ...


class BaseSerializer(abc.ABC):
    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        """Iterate over fragments of the content."""
        ...

    @abc.abstractmethod
    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        ...


class BaseCollection(abc.ABC, Iterable[TData]):
    """Declaration of collection properties."""

    name: str
    params: dict[str, Any]

    columns: BaseColumns
    data: BaseData[TData]
    filters: BaseFilters
    pager: BasePager
    serializer: BaseSerializer


class BaseFilters(abc.ABC):
    """Declaration of filters properties."""

    filters: list[Filter[Any]]
    actions: list[Filter[Any]]


class Filter(TypedDict, Generic[TFilterOptions]):
    """Filter details."""

    name: str
    type: str
    options: TFilterOptions
