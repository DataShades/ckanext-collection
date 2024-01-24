from __future__ import annotations

import abc
from collections.abc import Sized
from typing import Any, Callable, Generic, Iterable, Literal, Sequence, Union

from typing_extensions import NotRequired, TypeAlias, TypedDict, TypeVar

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
    searchable: set[str]
    labels: dict[str, str]
    serializers: dict[str, list[tuple[str, dict[str, Any]]]]

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

    @abc.abstractmethod
    def serialize_value(self, value: Any, name: str, record: Any):
        """Transform record's value into its serialized form."""
        ...

    @abc.abstractmethod
    def dictize_row(self, row: Any) -> dict[str, Any]:
        """Transform single data record into serializable dictionary."""
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


class BaseFilters(abc.ABC, Service):
    """Declaration of filters properties."""

    filters: Sequence[Filter[Any]]
    actions: Sequence[Filter[Any]]

    @property
    def service_name(self):
        return "filters"


class Filter(TypedDict, Generic[TFilterOptions]):
    """Filter details."""

    name: str
    type: Any
    options: TFilterOptions


class _SelectOptions(TypedDict):
    text: str
    value: str


class SelectFilterOptions(TypedDict):
    label: str
    options: Sequence[_SelectOptions]


class InputFilterOptions(TypedDict):
    label: str
    placeholder: NotRequired[str]
    type: NotRequired[str]


class ButtonFilterOptions(TypedDict):
    label: str
    type: NotRequired[str]


class StaticLinkFilterOptions(TypedDict):
    label: str
    href: str


class DynamicLinkFilterOptions(TypedDict):
    label: str
    endpoint: str
    kwargs: dict[str, Any]


class SelectFilter(Filter[SelectFilterOptions]):
    type: Literal["select"]


class InputFilter(Filter[InputFilterOptions]):
    type: Literal["input"]


class ButtonFilter(Filter[ButtonFilterOptions]):
    type: Literal["button"]


class LinkFilter(Filter[Union[StaticLinkFilterOptions, DynamicLinkFilterOptions]]):
    type: Literal["link"]


ValueSerializer: TypeAlias = Callable[
    [Any, "dict[str, Any]", str, Any, BaseSerializer],
    Any,
]
