from __future__ import annotations

from ckanext.collection.utils.data import ApiData, ApiListData, ApiSearchData

from .base import Collection


class ApiCollection(Collection):
    DataFactory = ApiData


class ApiSearchCollection(ApiCollection):
    DataFactory = ApiSearchData


class ApiListCollection(ApiCollection):
    DataFactory = ApiListData
