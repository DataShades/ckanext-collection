# Abstract service

It's a concept, not a real service. This concept is used as a base by
absolutely every service of any collection. And if you decide to introduce a
brand new service, it will extend the base abstract service.

Because this abstract service is used by every service type, it defines a
number of standard traits of every service. Everything you'll learn in this
chapter can be applied to every service you see in a real application.

## Service

The abstract service actually consists of two classes. The first one is
`types.Service`. This is an abrstract class, which contains abstract property
`service_name`. The property identifies the name of the service inside the
collection.

The base `data.Data` class implements `types.Service` and its implementation of
`service_name` returns `data`. The base `serialize.Serializer` has
`service_name` that returns `serializer`. And every other type of service does
similar thing.

Because of this, collection knows, where to put the service in the following
code snippet:

```python
src = collection.Collection(data_factory=data.StaticData)
dest = collection.Collection()
dest.replace_service(src.data)
```

We don't tell collection, that we are replacing the data service. But because
the object passed into `replace_service` has `service_name` property,
collection can recognize it and assign into correct attribute.

If someone create a service that provides Solr connection, this service will
get `service_name` property with value `solr`. And because of it, collection
will keep any instance of such service as `col.solr`.

## Domain

The second component of abstract service is `Domain`. `Domain` and
`types.Service` are always used together. Every non-abstract service is
subclassed from both `Domain` and `types.Service`.

`Domain` provides a set of convenient features for services.

First, and probably most important, it defines the constructor of service as
method with one positional-only argument(the collection) and any number of
keyword-only arguments(settings). Thanks to `Domain`, when service is
initialized, it's automatically attached to collection.

```pycon
>>> col = collection.Collection()
>>> data.StaticData(col)
>>> isinstance(col.data, data.StaticData)
True
```

Settings are processed in a special way and will be described further inside
[settings](#settings) section.

`Domain` exposes collection as `attached` property of the service. This is the
two-way reference: collection contains link to its services and every service
contains a link to the collection.

```pycon
>>> col = collection.Collection()
>>> col.data.attached is col
True
>>> col.columns.attached is col
True
>>> col.pager.attached is col
True
```

And `Domain` provides `with_attributes` classmethod inside service. This method
creates a subclass of the caller with overridden attributes.

```pycon
>>> MyData = data.Data.with_attributes(a=1, b=2)
>>> col = collection.Collection(data_factory=MyData)
>>> col.data.a
1
>>> col`.data.b
2
```

## Settings

Service settings are passed as keyword-only arguments to service constructor or
as `<SERVICE>_settings` dictionary to collection constructor. In both cases
settings are processed in the same way. Service keeps known parameters and
ignores everything else.

That's a rule. Service does not keeps all the settings, it stores only settings
that are registered inside the service.

/// admonition
    type: example

As `Data` has no settings, the whole `data_settings` is ignored.

```pycon
>>> col = collection.Collection(
>>>     data_factory=data.Data,
>>>     data_settings={"a": 1, "b": 2, "data": [1, 2, 3]},
>>> )
>>> hasattr(col.data, "a")
False
>>> hasattr(col.data, "b")
False
>>> hasattr(col.data, "c")
False
```
///

Every *configurable attribute* of the service must be registered first, and
only then you can set it via settings.

To register the attribute, you have to create it inside class definition. And
its value must be generated by `configurable_attribute` function.

/// admonition
    type: example

```python
from ckanext.collection.shared import collection, data, configurable_attribute

class MyData(data.Data):
    a = configurable_attribute("default a") # (1)!
    b = configurable_attribute(default_factory=lambda self: "default b") # (2)!
    c = configurable_attribute() # (3)!
```

1. Positional argument is used as default value for the attribute
2. Named `default_factory` accepts a function that receives the service
   instance and returns default value of attribute.
3. If no default provided, attribute becomes mandatory and will cause an
   exception if missing during initialization of service.

///

`configurable_attribute` accepts either static default value or a function that
produces default value. Such function must be passed via named argument
`default_factory` and must accept the only parameter: the service itself. If
`configurable_attribute` is called without arguments, it registers a required
attribute and service cannot be initialized without this attribute.

/// warning

It's not allowed to use other configurable attributes inside `default_factory`
of configurable attribute. The initialization order of configurable attributes
is not defined at the moment. There are not guarantees that referred attribute
is already initialized when `default_factory` is called.

///

Any configurable attribute can be assigned via settings. If you try using
settings with the class from the example above, registered attributes will be
picked and added to the service:

```pycon
>>> col = collection.Collection(
>>>     data_factory=MyData,
>>>     data_settings={"a": 1, "b": 2, "c": [1, 2, 3]},
>>> )
>>> col.data.a
1
>>> col.data.b
2
>>> col.data.c
[1, 2, 3]
```

/// tip

`with_attributes` also can create configurable attributes.

```python

from ckanext.collection.shared import data, configurable_attribute

MyData = data.Data.with_attributes(
    a=configurable_attribute("default a"),
    b=configurable_attribute(default_factory=lambda self: "default b"),
    c=configurable_attribute(),
)
```

///