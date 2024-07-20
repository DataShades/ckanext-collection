# Collection

## Overview

Collection works as a proxy between user and collection's services. It hides
internal complexity and simplifies access to data.

The very base collection contains no data. It can be initialized using
`Collection` constructor.

```pycon
>>> col = collection.Collection()
>>> list(col)
[]
```

Constructor of collection accepts two positional arguments:

* `name`: string containing letters, numbers, underscores and hyphens
* `params`: dictionary that can be used by services. There are no rules that
  define, how exactly params are used and whether or not they are used at
  all. Everything depends on services. For example, pager *usually* checks
  `page` and `rows_per_page` inside `params`. Data service often uses fields
  from `params` to filter data.

/// note

`params` depend on collection name. If the name is empty, params are used
without changes. If name is not empty, params are filtered and
transformed. First, any member of params that is not prefixed with collection
name and colon is removed. Then, the prefix is removed.

```pycon
>>> col = collection.Collection("", {"a": 1, "xxx:b": 2, "yyy:c": 3}) # (1)!
>>> col.params
{"a": 1, "xxx:b": 2, "yyy:c": 3}
>>> col = collection.Collection("xxx", {"a": 1, "xxx:b": 2, "yyy:c": 3}) # (2)!
>>> col.params
{"b": 2}
>>> col = collection.Collection("yyy", {"a": 1, "xxx:b": 2, "yyy:c": 3}) # (3)!
>>> col.params
{"c": 3}
```

1. All parameter are kept because collection has no name.
2. Only `xxx:b` is kept and its name transformed to just `b`, because
   collection has name `xxx`.
3. Only `yyy:c` is kept and its name transformed to just `c`, because
   collection has name `yyy`.

///


/// details | Why `params` are transformed?
    type: tip

As long as collection is initialized manually and don't have a name, you don't
need to think about `params` transformation.

```pycon
>>> col = collection.Collection("", {"a": 1, "xxx:b": 2, "yyy:c": 3})
>>> col.params
{"a": 1, "xxx:b": 2, "yyy:c": 3}
```

Transformation becomes important, whn you initialize registered *named*
collection via `get_collection`

```pycon
>>> col = get_collection(
>>>    "my-collection",
>>>    {"a": 1, "my-collection:b": 2},
>>> )
>>> col.params
{"b": 2}
```

This design decision was made to simplify rendering conllections on webpages.

Imagine the page that renders `users` and `packages` collection. These
collections are rendered as tables with pagination and view code looks like this:

```python
import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

@route(...)
def users_and_packages():
    params = parse_params(tk.request.args)

    users = get_collection("users", params)
    packages = get_collection("packages", params)

    return tk.render(template, {
        "users": users,
        "packages": packages,
    })

```

Because `params` uses collection name as prefix, it's possible to paginate
collections separately. Query string `?users:page=2&packages:page=8` parsed
into `params` dictionary on the first line of view. This dictionary contains
both page values with prefixes. When `users` and `packages` collections
initialized, they pick only relevant values from `params`, so `users` takes
`page=2` and `packages` takes `page=8`.

In this way, `params` flow naturally from user into collection. When you are
initializing collections in code, most likely you'll interact with collection
classes instead of `get_collection`, so you can leave collection name empty and
keep all `params`:

```python
col = MyCollection("", {...})
```

And when you must use `get_collection` with named collection, but want to pass
all `params` into collection, you can easily add prefixes yoursef:

```pycon
>>> data = {"a": 1, "b": 2}
>>> name = "my-collection"
>>> col = get_collection(name, {f"{name}:{k}": v for k, v in data.items()})
>>> col.params
{"a": 1, "b": 2}
```

And to make it even simpler, `get_collection` accepts `prefix_params` as 3rd
positional argument. When this flag is enabled, prefixes are added
automatically, so you can achieve the same effect as in snippet above using
short version:

```pycon
>>> col = get_collection("my-collection", {"a": 1, "b": 2}, True)
>>> col.params
{"a": 1, "b": 2}
```


///

## Initialization

When a collection is created, it initializes services using service factories
and service settings. `data` service is initialized using
`Collection.DataFactory` class and `data_settings`, `serializer` is initialized
using `Collection.SerializerService` and `serializer_settings`, etc.

This logic creates a workflow for defining new collections. Create a subclass
of base Collection and override `*Factory` of this new class.

/// admonition
    type: example

```python
class MyCollection(collection.Collection):
    DataFactory = data.StaticData
```

```pycon
>>> col = MyCollection()
>>> isinstance(col.data, data.StaticData)
True
```

///


Now you only need to find a suitable class for the service and job is done.

But as soon as you choose the class, you'll notice, that majority of service
factories must be configured before using. For example, the `StaticData` used
in the example above produces records using iterable source. And this iterable
must be configured, or you'll get just empty list from `StaticData`:

```pycon
>>> col = MyCollection()
>>> list(col)
[]
```

Configuration for services can be specified using keyword-only arguments of the
collection's constructor. Pass `<SERVICE>_settings` dictionary to collection
and this dictionary will be used as service settings. `data_settings={...}` is
passed to data service, `pager_settings={...}` is passed to pager service,
etc.

Iterable with items is controlled by `data` parameter of `StatiData`. And it
means you need to pass `data_settings={"data": [1, 2, 3]}` to collection
constructor, if you want to use `[1, 2, 3]` as a data collection.

/// admonition
    type: example

```pycon
>>> col = MyCollection(data_settings={"data": [1, 2, 3]})
>>> list(col)
[1, 2, 3]
```
///

Instead of specifying `data` every time, you can create a derived class from
`StaticData` and replace the default value of `data`.

/// admonition
    type: example

```python
class MyData(data.StaticData):
    data = [1, 2, 3]

class MyCollection(collection.Collection):
    DataFactory = MyData
```

```pycon
>>> col = MyCollection()
>>> list(col)
[1, 2, 3]
```
///

New classes are created quite often with ckanext-collection. And every existing
service has a shortcut for creating its derivable with customized attributes.

Whenever you need to extend parent service and set `attr` to `value` in the
child class, use `with_attributes` classmethod of the parent service.

/// admonition
    type: example

```python
MyData = data.StaticData.with_attributes(data=[1, 2, 3])

class MyCollection(collection.Collection):
    DataFactory = MyData
```

```pycon
>>> col = MyCollection()
>>> list(col)
[1, 2, 3]
```
///


And, in the same way you can pass settings for services, you can also specify
factories when collection is initialized. Every `<SERVICE>_factory` paramterer
of the collection's constructor overrides corresponding factory of the
collection: `data_factory=StaticData` sets `DataFactory = StaticData`,
`serializer_factory=CsvSerializer` sets `SerializerFactory = CsvSerializer`,
etc.


/// admonition
    type: example

Instead of creating a new classes from previous examples, you could use the
following code:

```python
>>> col = collection.Collection(
>>>     data_factory=data.StaticData,
>>>     data_settings={"data": [1, 2, 3]},
>>> )
>>> list(col)
[1, 2, 3]
```

Or even:

```python
>>> col = collection.Collection(
>>>     data_factory=data.StaticData.with_attributes(
>>>         data=[1, 2, 3],
>>>     ),
>>> )
>>> list(col)
[1, 2, 3]
```

This form is convenient when you experimenting with collections or creating
them dynamically. But more often you'll create a separate class for collection
and services. Using separate classes is more readable and flexible, as you keep
all the derived classes and can combine/reuse them in future.

///

/// warning

`*_factory` accepts **a class** that can be used to initialize the service. You can
use `data.StaticData`, because it's a class. Or you can use
`data.StaticData.with_attributes(data=[1, 2, 3])`, because this method creates
a new class.

But you cannot use `data_factory=data.StaticData()` with parenthesis, because
in this way you create **an instance** of the service and this instance cannot
be used to initialize another instance.

Remember: factory is a class; service is an object of this class.
///


## Usage

Collections are not very impressive. You literally can create the collection
and then you can iterate over a single page of collection results. But this
must be exactly what you are doing most of the time. In a well defined
collection, you don't need to access any services, apart from serializer.

Let's use collection of all users from DB.

/// admonition | Definition of collection
    type: abstract

```python
from ckan import model
from ckanext.collection.shared import collection, data

class Users(collection.Collection):
    DataFactory = data.ModelData.with_attributes(
        model=model.User,
        is_scalar=True,
    )
```
///

Initialize this collection without arguments to work with 1st-10th users `#!py3
users = Users()`.

You can use direct access to data service to get users from 11th: `#!py3
users.data[10:20]`. But you can also initialize the collection for the second
page: `#!py3 users = Users(pager_settings={"page": 2})`.

If you know that you'll process more than 10 users at once, it's still possible
to avoid direct access to data. Just set `rows_per_page` option of the pager:
`#!py3 users = Users(pager_settings={"rows_per_page": 100})`

/// tip

`ModelData` supports search by filterable columns. For example, if you want to
search users by `sysadmin` flag, configure columns service and add `sysadmin`
to the `Columns.filterable`:

```pycon
>>> sysadmins = Users(
>>>     "",
>>>     {"sysadmin": True},
>>>     columns_factory=columns.Columns.with_attributes(filterable={"sysadmin"})
>>> )
>>> all(user.sysadmin for user in sysadmins)
True
```

Obviously, you can just create plain collection of users and pick sysadmins
manually, iterating over `users.data`. And it would be absolutely normal
solution, that works with any collection.

```pycon
>>> sysadmins = [
>>>     user for user in Users()
>>>     if user.sysadmin
>>> ]
```

But some services have more efficient ways to work with data, other than naive
iteration. In case of `ModelData`, specifying `Columns.filterable` and using
params of collection to filter the data produces optimized SQL query that
fetches only required rows from DB.

Always check documentation of the collection and its services and there is a
chance that you'll find more efficient solution of your problem.

///


## Replacing the service

/// warning

This functionality is experimental and can change in future. Use it only if you
see no other ways to achieve the result.

///

It's possible to replace collection services after collection
initialized. There are two ways to do it: by creating a new instance of the
service and by expropriation service from the different collection.

Creating a new service is staightforward. Service's constructor accepts
collection as first positional argument and unlimited number of keyword-only
arguments which are collected as service's settings.

/// admonition
    type: example

```pycon
>>> col = collection.Collection()
>>> new_service = data.StaticData(col, data=[1, 2, 3])
>>> new_service is col.data
True
```

The above example approximately the same as the following code

```python

col = collection.Collection(
    data_factory=data.StaticData,
    data_settings={"data": [1, 2, 3]},
)
```
///

When a new service is created, old service instance is discarded and the new
one is attached to the collection. As you can see in the example, there is no
need to assign the service into collection's `data` attribute. We just
initialize the service and it automatically got into the right place.

/// warning

Never use discarded service. It still has references to its parent collection,
but collection itself does not recognize the discarded service anymore. This
one-way reference often produce strange behavior.

///


Reusing service from the existing collection is also simple. Just call
`replace_service` of the new collection, that will take the service, and pass
into it service that must be attached to collection.

/// admonition
    type: example

```pycon
>>> src = collection.Collection(data_factory=data.StaticData)
>>> dest = collection.Collection()
>>> dest.replace_service(src.data)
>>> isinstance(dest.data, data.StaticData)
True
```
///

`replace_service` also detaches old service and attaches the new one to
collection. And, on top of this, the new service *is detached from its original
collection*. It makes original collection unusable, unless you give it a new
service instance instead.

/// warning

Collection that lost its service because it was transfered to another
collection, must not be used anymore. Just as with detached services, old
collection still contains reference to its detached service, but service
becomes the part of different collection and has no back reference to old
collection. Using collection with such kind of one-way reference to service
ofter produces strange behavior.

If you want to use collection that lost its service, initialize a new service
that will replace the old instance:

```python
src = collection.Collection(data_factory=data.StaticData)
dest = collection.Collection()
dest.replace_service(src.data)

# right now `src` cannot be used

data.StaticData(src)

# now `src` got a new data service and it can be used again
```


///
