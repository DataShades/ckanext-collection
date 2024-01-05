"""Logic used across collection utilities.

"""
from __future__ import annotations

import abc
import dataclasses
import inspect
from collections.abc import Hashable
from typing import Any, Callable, Generic, TypeVar, cast

import ckan.plugins.toolkit as tk

from ckanext.collection.types import (
    BaseCollection,
    CollectionFactory,
    TDataCollection,
    Service,
)

T = TypeVar("T")
SENTINEL = object()


@dataclasses.dataclass
class Registry(Generic[T]):
    members: dict[Hashable, T]

    def reset(self):
        self.members.clear()

    def register(self, name: Hashable, member: T):
        self.members[name] = member

    def get(self, name: Hashable) -> T | None:
        return self.members.get(name)


collection_registry: Registry[CollectionFactory] = Registry({})


class AttachTrait(abc.ABC, Generic[TDataCollection]):
    """Attach collection to the current object.

    `_attach` method must be called as early as possible in the constructor of
    the derived class. It makes collection available inside an instance via
    `attached` property. Because initialization of collection utilities often
    relies on collection details, you should call `_attach` before any other
    logic.

    Example:

    >>> class Impl(AttachTrait):
    >>>     def __init__(self, collection):
    >>>         self._attach(collection)
    >>>
    >>> collection = object()
    >>> obj = Impl(collection)
    >>> assert obj.attached is collection

    """

    __collection: TDataCollection

    def _attach(self, obj: TDataCollection):
        self.__collection = obj
        if isinstance(self, Service):
            # this block allows attaching services to non-collections. Mainly
            # it's used in tests
            replace_service = getattr(obj, "replace_service", None)
            if replace_service:
                replace_service(self)

    @property
    def attached(self) -> TDataCollection:
        return self.__collection


class AttrSettingsTrait:
    """Get attribute value from settings for the current utility object.

    To mark an attribute as configurable, declare it using
    `configurable_attribute` function:

    >>> class Impl(AttrSettingsTrait):
    >>>     attr = configurable_attribute("default value")

    To initialize attributes, call `_gather_settings` with dictionary
    containing attribute values. If attribute is available in the dictionary,
    dictionary value moved into attribute:

    >>> obj = Impl()
    >>> obj._gather_settings({"attr": "custom value"})
    >>> assert obj.attr == "custom value"

    If dictionary doesn't have a member named after the attribute, default
    value/factory is used to initialize the attribute

    >>> obj = Impl()
    >>> obj._gather_settings({})
    >>> assert obj.attr == "default value"

    `_gather_settings` can be called multiple times to reset/modify
    settings. Keep in mind, that every call processes all the configurable
    attributes of the instance. For example, if instance has `a` and `b`
    configurable attributes and you call `_gather_settings` with `{"a": 1}`
    first, and then with `{"b": 2}`, value of `a` will be removed and replaced
    by the default:

    >>> class Impl(AttrSettingsTrait):
    >>>     a = configurable_attribute(None)
    >>>     b = configurable_attribute(None)
    >>>
    >>> obj = Impl()
    >>> obj._gather_settings({"a": 1})
    >>> assert obj.a == 1
    >>> assert obj.b is None
    >>>
    >>> obj._gather_settings({"b": 2})
    >>> assert obj.a == None
    >>> assert obj.b is 2
    >>>
    >>> obj._gather_settings({"b": 2, "a": 1})
    >>> assert obj.a == 1
    >>> assert obj.b == 2
    >>>
    >>> obj._gather_settings({})
    >>> assert obj.a is None
    >>> assert obj.b is None

    The best place to gather settings, early in the constructor, right after
    `_attach`. Example:

    >>> class Impl(AttachTrait, AttrSettingsTrait):
    >>>     a = configurable_attribute(None)
    >>>     b = configurable_attribute(None)
    >>>
    >>>     def __init__(self, collection, **kwargs):
    >>>         self._attach(collection)
    >>>         self._gather_settings(kwargs)

    """

    def _gather_settings(self, kwargs: dict[str, Any]):
        for k, attr in inspect.getmembers(
            type(self),
            lambda attr: isinstance(attr, _InitAttr),
        ):
            if k in kwargs:
                setattr(self, k, kwargs.pop(k))

            else:
                setattr(self, k, attr.get_default(self))


@dataclasses.dataclass
class _InitAttr:
    default: Any = SENTINEL
    default_factory: Callable[[Any], Any] = cast(Any, SENTINEL)

    def __post_init__(self):
        if self.default is not self.default_factory:
            return

        msg = "Either `default` or `default_factory` must be provided"
        raise ValueError(msg)

    def get_default(self, obj: Any):
        if self.default is SENTINEL:
            return self.default_factory(obj)

        return self.default


def configurable_attribute(
    default: T | object = SENTINEL,
    default_factory: Callable[[Any], T] | object = SENTINEL,
) -> T:
    """Declare configurable attribute.

    Example:

    >>> class DataFactory(Data):
    >>>     private = configurable_attribute(False)
    >>>
    >>> data = DataFactory(None, private=True)
    >>> assert data.private
    """
    return cast(T, _InitAttr(default, cast(Any, default_factory)))


class UserTrait(AttrSettingsTrait):
    """Add configurable `user` attribute, with default set to
    `current_user.name`.

    """

    user = configurable_attribute(
        default_factory=lambda str: tk.current_user.name if tk.current_user else "",
    )


class Domain(AttachTrait[TDataCollection], AttrSettingsTrait):
    """Standard initializer for collection utilities.

    Used as base class for utility instances created during collection
    initialization(e.g Pager, Columns, Filters, Data).

    Defines standard constructor signature, attaches collection to the utility
    instance and collects settings.

    """

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        self._attach(obj)
        self._gather_settings(kwargs)

    @classmethod
    def with_attributes(cls: type[T], **attributes: Any) -> type[T]:
        """Create anonymous derivable of the class with overriden attributes.

        This is a shortcut for defining a proper subclass of the domain:

        >>> class Parent(Domain):
        >>>     prop = "parent value"
        >>>
        >>> class Child(Parent):
        >>>     prop = "child value"
        >>>
        >>> # equivalent
        >>> Child = Parent.with_attributes(prop="child value")
        """
        return cast("type[T]", type(cls.__name__, (cls,), attributes))


def parse_sort(sort: str) -> tuple[str, bool]:
    """Parse sort as column and sorting direction.

    Turn `-name` and `name desc` into `(name, True)`. Everything else turns
    into `(name, False)`.

    """
    desc = False
    if sort.startswith("-"):
        sort = sort[1:]
        desc = True

    elif len(parts := sort.split()) == 2:
        sort, direction = parts

        if direction.lower() == "desc":
            desc = True

    return sort, desc


def get_collection(name: str, params: dict[str, Any]) -> BaseCollection[Any] | None:
    if factory := collection_registry.get(name):
        return factory(name, params)

    return None
