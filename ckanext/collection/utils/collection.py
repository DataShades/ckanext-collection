from __future__ import annotations
from typing import Any
from typing_extensions import Self

from .columns import Columns
from .data import Data, ModelData
from .pager import Pager, ClassicPager
from .serialize import Serializer
from .filter import Filters


class BaseCollection:
    """Base data source for interactive tables.

    Contains the following information:
    * data itself
    * available filters
    * details about table columns
    * search params
    * pagination details

    In most scenarious, you'll create a subclass of the collection with
    different factories. If you have `ApiData` subclass of `Data`, which
    produces data using CKAN API, and `ApiFilters` subclass of `Filters`, which
    produce values for UI filters you can create the following collection
    subclass:

        class ApiCollection(ApiData):
            DataFactory = ApiData
            FiltersFactory = ApiFilters

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

        self.pager = self._instantiate("pager", kwargs)
        self.columns = self._instantiate("columns", kwargs)

        self.filters = self._instantiate("filters", kwargs)
        self.data = self._instantiate("data", kwargs)
        self.serializer = self._instantiate("serializer", kwargs)

    def _instantiate(self, name: str, kwargs: dict[str, Any]) -> Any:
        if factory := kwargs.get(f"{name}_factory"):
            fn = "".join(p.capitalize() for p in name.split("_"))
            setattr(self, fn + "Factory", factory)

        value = kwargs.get(f"{name}_instance")
        if not value:
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
