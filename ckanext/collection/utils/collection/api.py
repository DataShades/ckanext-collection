from __future__ import annotations

from ckanext.collection import types
from ckanext.collection.utils.data import ApiData, ApiListData, ApiSearchData

from .base import Collection


class ApiCollection(Collection[types.TData]):
    DataFactory = ApiData


class ApiSearchCollection(ApiCollection[types.TData]):
    DataFactory = ApiSearchData


class ApiListCollection(ApiCollection[types.TData]):
    DataFactory = ApiListData
