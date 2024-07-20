from __future__ import annotations

import copy
import logging
from typing import Any, Callable, Iterable, Iterator

import ckan.plugins.toolkit as tk
from ckan.types import Context

from ckanext.collection import internal, types

from .base import Data

log = logging.getLogger(__name__)


class ApiData(Data[types.TData, types.TDataCollection], internal.UserTrait):
    """API data source.

    This base class is suitable for building API calls. Its `compute_data`
    makes the single request to the specified API action and yields items from
    the response.

    Attributes:
        action: API action that returns the data
        payload: parameters passed to the action
        ignore_auth: skip authorization checks
        user (str): name of the user for the action. Default: `tk.current_user.name`

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.ApiData,
        >>>     data_settings={"action": "group_list_authz", "user": "default"},
        >>> )
        >>> list(col)
        [{...}, {...}]
        ```

    """

    action: str = internal.configurable_attribute()
    payload: dict[str, Any] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )
    ignore_auth: bool = internal.configurable_attribute(False)

    def make_context(self):
        return Context(user=self.user, ignore_auth=self.ignore_auth)

    def prepare_payload(self) -> dict[str, Any]:
        return copy.deepcopy(self.payload)

    def compute_data(self):
        action = tk.get_action(self.action)
        return action(self.make_context(), self.prepare_payload())


class ApiSearchData(ApiData[types.TData, types.TDataCollection]):
    """API data source optimized for package_search-like actions.

    This class expects that API action accepts `start` and `rows` parameters
    that controls offset and limit. And result of the action must contain
    `count` and `results` keys.

    This data service can iterate over huge number of items, reading just few
    of them into the memory at once.

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.ApiSearchData,
        >>>     data_settings={
        >>>         "action": "package_search",
        >>>         "payload": {"q": "res_format:CSV"},
        >>>     },
        >>> )
        >>> list(col)
        [{...}, {...}]
        ```
    """

    def prepare_payload(self) -> dict[str, Any]:
        payload = super().prepare_payload()
        return dict(
            payload,
            **self.get_filters(),
            **self.get_sort(),
        )

    def get_filters(self) -> dict[str, str]:
        return {}

    def get_sort(self) -> dict[str, str]:
        sort = self.attached.params.get("sort")
        if not sort:
            return {}

        column, desc = internal.parse_sort(sort)

        if column not in self.attached.columns.sortable:
            log.warning("Unexpected sort value: %s", sort)
            return {}

        direction = "desc" if desc else "asc"
        return {"sort": f"{column} {direction}"}

    def get_action(self) -> Callable[[Context, dict[str, Any]], Any]:
        return tk.get_action(self.action)

    def compute_data(self):
        action = self.get_action()
        return action(self.make_context(), dict(self.prepare_payload(), rows=0))

    def compute_total(self, data: dict[str, Any]) -> int:
        return data["count"]

    def range(self, start: int, end: int) -> Iterable[types.TData]:
        action = self.get_action()
        return action(
            self.make_context(),
            dict(self.prepare_payload(), rows=end - start, start=start),
        )["results"]

    def at(self, index: int) -> types.TData:
        action = self.get_action()
        return action(
            self.make_context(),
            dict(self.prepare_payload(), rows=1, start=index),
        )["results"][0]

    def __iter__(self) -> Iterator[types.TData]:
        action = self.get_action()
        context = self.make_context()
        start = 0
        while True:
            result = action(context, dict(self.prepare_payload(), start=start))

            yield from result["results"]
            start += len(result["results"])

            if start >= result["count"] or not result["results"]:
                break
