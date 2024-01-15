from __future__ import annotations

from typing import Any, Iterator, overload

from typing_extensions import Self

from ckanext.collection import shared, types

from .columns import Columns
from .data import ApiData, ApiListData, ApiSearchData, Data, ModelData, StaticData
from .filters import Filters
from .pager import ClassicPager, Pager
from .serialize import Serializer


class Collection(types.BaseCollection[types.TData]):
    """Base data collection.

    Contains the following information:
    * data itself
    * available filters
    * details about table columns
    * pagination details
    * serializer instance

    In most scenarious, you'll create a subclass of the collection with
    different factories. If you have `ApiData` subclass of `Data`, which
    produces data using CKAN API, you can create the following collection
    subclass:

    >>> class ApiCollection(Collection):
    >>>     DataFactory = ApiData

    Collections can be created on demand, using constructor parameters. For
    example, ApiCollection mentioned above can be instantiated even without
    dedicated class:

    >>> api_collection = Collection(
    >>>     data_factory=ApiData,
    >>> )

    Subclasses are more flexible, than dynamic collections. They allow
    overriding and enhancing different aspects of collection. But creating
    collections on demand may be more convenient if you need a number of
    similar collections and prefer not to bloat the codebase with almost
    identical classes.

    Apart from mandatory `name` and `params` arguments, all arguments to the
    constructor must be named and follow one of three patterns:

    * SMTH_factory - class used to instantiate an attribute. Example:

      >>> Colection(data_factory=ModelData)
      >>> Colection(serializer_factory=JsonSerializer)

    * SMTH_instance - object assigned to the attribute. If present, factory is
      ignored. Example:

      >>> col = Colection()
      >>> another_col = Colection(pager_instance=col.pager)

    * SMTH_settings - collection of named arguments passed into constructor of
      the corresponding attribute. Example

      >>> Collection(pager_settings={"rows_per_page": 100})
      >>> Collection(columns_settings={"names": ["title", "notes"]})

    Attributes:
      name: unique name of the collection
      params: data used for search/pagination/sorting/etc.

    """

    # keep these classes here to simplify overrides
    ColumnsFactory: type[Columns[Self]] = Columns
    DataFactory: type[Data[types.TData, Self]] = Data
    FiltersFactory: type[Filters[Self]] = Filters
    SerializerFactory: type[Serializer[Self]] = Serializer
    PagerFactory: type[Pager[Self]] = ClassicPager

    _service_names: tuple[str, ...] = (
        "columns",
        "pager",
        "filters",
        "data",
        "serializer",
    )

    def __init__(self, name: str, params: dict[str, Any], /, **kwargs: Any):
        """Use name to pick only relevant parameters.

        When multiple collections rendered on the same page, the use format
        `collection:param` to avoid conflicts with parameters from different
        collections.

        """
        self.name = name

        if self.name:
            params = {
                k[len(self.name) + 1 :]: v
                for k, v in params.items()
                if k.startswith(f"{self.name}:")
            }
        self.params = params

        for service in self._service_names:
            self.replace_service(self._instantiate(service, kwargs))

    def _instantiate(self, name: str, kwargs: dict[str, Any]) -> Any:
        if factory := kwargs.get(f"{name}_factory"):
            fn = "".join(p.capitalize() for p in name.split("_"))
            setattr(self, fn + "Factory", factory)

        value: shared.Domain[Any] | None = kwargs.get(f"{name}_instance")
        if value is None:
            maker = getattr(self, f"make_{name}")
            value = maker(**kwargs.get(f"{name}_settings", {}))

        else:
            value._attach(self)  # pyright: ignore [reportPrivateUsage]

        return value

    @overload
    def replace_service(self, service: types.BaseColumns) -> types.BaseColumns | None:
        ...

    @overload
    def replace_service(
        self,
        service: types.BaseData[Any],
    ) -> types.BaseData[Any] | None:
        ...

    @overload
    def replace_service(self, service: types.BasePager) -> types.BasePager | None:
        ...

    @overload
    def replace_service(self, service: types.BaseFilters) -> types.BaseFilters | None:
        ...

    @overload
    def replace_service(
        self,
        service: types.BaseSerializer,
    ) -> types.BaseSerializer | None:
        ...

    def replace_service(self, service: types.Service) -> types.Service | None:
        """Attach service to collection"""
        old_service = getattr(self, service.service_name, None)
        setattr(self, service.service_name, service)
        return old_service

    def __iter__(self) -> Iterator[types.TData]:
        yield from self.data.range(self.pager.start, self.pager.end)

    def make_serializer(self, **kwargs: Any) -> Serializer[Self]:
        """Return serializer."""
        return self.SerializerFactory(self, **kwargs)

    def make_pager(self, **kwargs: Any) -> Pager[Self]:
        """Return pager."""
        return self.PagerFactory(self, **kwargs)

    def make_columns(self, **kwargs: Any) -> Columns[Self]:
        """Return column details."""
        return self.ColumnsFactory(self, **kwargs)

    def make_filters(self, **kwargs: Any) -> Filters[Self]:
        """Return search filters."""
        return self.FiltersFactory(self, **kwargs)

    def make_data(self, **kwargs: Any) -> Data[types.TData, Self]:
        """Return search filters."""
        return self.DataFactory(self, **kwargs)


class StaticCollection(Collection[types.TData]):
    DataFactory = StaticData


class ModelCollection(Collection[types.TData]):
    DataFactory = ModelData


class ApiCollection(Collection[types.TData]):
    DataFactory = ApiData


class ApiSearchCollection(ApiCollection[types.TData]):
    DataFactory = ApiSearchData


class ApiListCollection(ApiCollection[types.TData]):
    DataFactory = ApiListData
