from __future__ import annotations

import abc
from collections.abc import Sized
from typing import Any, Callable, Generic, Iterable

from typing_extensions import TypeAlias, TypedDict, TypeVar

CollectionFactory: TypeAlias = "Callable[[str, dict[str, Any]], BaseCollection[Any]]"
TDataCollection = TypeVar("TDataCollection", bound="BaseCollection[Any]")
TFilterOptions = TypeVar("TFilterOptions")
TData = TypeVar("TData")


class Service:
    """Marker for service classes used by collection."""

    @abc.abstractproperty
    def service_name(self) -> str:
        """Name of the service instance used by collection."""
        ...


class BaseColumns(abc.ABC, Service):
    """Declaration of columns properties"""

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]

    @property
    def service_name(self):
        return "columns"


class BaseData(abc.ABC, Sized, Iterable[TData], Service):
    """Declaration of data properties."""

    @abc.abstractproperty
    def total(self) -> int:
        """Total number of data records."""
        ...

    @abc.abstractmethod
    def range(self, start: Any, end: Any) -> Iterable[TData]:
        """Slice data using specified limits."""
        ...

    @property
    def service_name(self):
        return "data"


class BasePager(abc.ABC, Service):
    """Declaration of pager properties"""

    params: dict[str, Any]

    @abc.abstractproperty
    def size(self) -> Any:
        """Range of the pager.

        In classic pager it may be the number of items per page. For date range
        pager, it can be a timespan within which we are searching for records.

        """
        ...

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

    @property
    def service_name(self):
        return "pager"


class BaseSerializer(abc.ABC, Service):
    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        """Iterate over fragments of the content."""
        ...

    @abc.abstractmethod
    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        ...

    @property
    def service_name(self):
        return "serializer"


class BaseCollection(abc.ABC, Iterable[TData]):
    """Declaration of collection properties."""

    name: str
    params: dict[str, Any]

    columns: BaseColumns
    data: BaseData[TData]
    filters: BaseFilters
    pager: BasePager
    serializer: BaseSerializer


class BaseFilters(abc.ABC, Service):
    """Declaration of filters properties."""

    filters: list[Filter[Any]]
    actions: list[Filter[Any]]

    @property
    def service_name(self):
        return "filters"


class Filter(TypedDict, Generic[TFilterOptions]):
    """Filter details."""

    name: str
    type: str
    options: TFilterOptions
