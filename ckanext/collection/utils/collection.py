from __future__ import annotations
from typing import Any
from typing_extensions import Self

from .columns import Columns
from .data import ApiData, Data, ModelData
from .pager import Pager, ClassicPager
from .serialize import Serializer
from .filter import Filters


class BaseCollection:
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

    >>> class ApiCollection(BaseCollection):
    >>>     DataFactory = ApiData
    >>>     PagerFactory = ClassicPager

    `PagerFactory` must be specified as well, because `BaseCollection` use
    abstract `Pager` by default and cannot be instantiated without actual pager
    implementation. You can use `Collection` as a base class instead, it
    already uses `ClassicPager`.

    `ClassicPager` contains pagination logic based on page number and number of
    items per page. It's mostly usable when data source accepts limit/offset
    parameters for slicing the data.

    Collections can be created on demand, using constructor parameters. For
    example, ApiCollection mentioned above can be instantiated even without
    dedicated class:

    >>> api_collection = BaseCollection(
    >>>     data_factory=ApiData,
    >>>     pager_factory=ClassicPager,
    >>> )

    Subclasses are more flexible, than dynamic collections. They allow
    overriding and enhancing different aspects of collection. But creating
    collections on demand may be more convenient if you need a number of
    similar collections and prefer not to bloat the codebase with almost
    identical classes.

    Apart from mandatory `name` and `params` arguments, all arguments to the
    constructor must be named and follow one of three patterns:

    * SMTH_factory - class used to instantiate an attribute. Example:

      >>> BaseColection(pager_factory=ClassicPager)
      >>> BaseColection(data_factory=ModelData)
      >>> BaseColection(serializer_factory=JsonSerializer)

    * SMTH_instance - object assigned to the attribute. If present, factory is
      ignored. Example:

      >>> col = Colection()
      >>> another_col = BaseColection(pager_instance=col.pager)

    * SMTH_settings - collection of named arguments passed into constructor of
      the corresponding attribute. Example

      >>> Collection(pager_settings={"rows_per_page": 100})
      >>> Collection(columns_settings={"names": ["title", "notes"]})

    Attributes:
      name: unique name of the collection
      params: data used for search/pagination/sorting/etc.

    """

    name: str
    params: dict[str, Any]

    # keep these classes here to simplify overrides
    ColumnsFactory: type[Columns[Self]] = Columns
    DataFactory: type[Data[Self]] = Data
    FiltersFactory: type[Filters[Self]] = Filters
    PagerFactory: type[Pager[Self]] = Pager
    SerializerFactory: type[Serializer[Self]] = Serializer

    columns: Columns[Self]
    data: Data[Self]
    filters: Filters[Self]
    pager: Pager[Self]
    serializer: Serializer[Self]

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
        kwargs.setdefault("pager_settings", {"params": params})

        self.columns = self._instantiate("columns", kwargs)
        self.pager = self._instantiate("pager", kwargs)
        self.filters = self._instantiate("filters", kwargs)
        self.data = self._instantiate("data", kwargs)
        self.serializer = self._instantiate("serializer", kwargs)

    def _instantiate(self, name: str, kwargs: dict[str, Any]) -> Any:
        if factory := kwargs.get(f"{name}_factory"):
            fn = "".join(p.capitalize() for p in name.split("_"))
            setattr(self, fn + "Factory", factory)

        value = kwargs.get(f"{name}_instance")
        if value:
            value.attach(self)

        else:
            maker = getattr(self, f"make_{name}")
            value = maker(**kwargs.get(f"{name}_settings", {}))

        return value

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

    def make_data(self, **kwargs: Any) -> Data[Self]:
        """Return search filters."""
        return self.DataFactory(self, **kwargs)


class Collection(BaseCollection):
    PagerFactory = ClassicPager


class ModelCollection(Collection):
    DataFactory = ModelData


class ApiCollection(Collection):
    DataFactory = ApiData
