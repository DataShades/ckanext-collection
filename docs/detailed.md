# Deep dive

### Overview

The goal of this plugin is to supply you with generic classes for processing
collections of data. As result, it doesn't do much out of the box and you have
to write some code to see a result.

Majority of useful classes are available inside `ckanext.collection.utils`
module and all examples bellow require the following line in the beginning of
the script: `from ckanext.collection.utils import *`.

Let's start with the basics. `ckanext-collection` defines a few collections for
different puproses. The most basic collection is `Collection`, but it has no
value without customization, so we'll start from `StaticCollection`:

```python
col = StaticCollection("name", {})
```

Constructor of any collection has two mandatory arguments: name and
parameters. Name is mostly used internally and consists of any combination of
letters, digits, hyphens and underscores. Parameters are passed inside the
dictionary and they change the content of the collection.

In the most basic scenario, collection represents a number of similar items:
datasets, users, organizations, dictionaries, numbers, etc. As result, it can
be transformed into list or iterated over:

```python
list(col)

for item in col:
    print(item)
```

Our test collection is empty at the moment, so you will not see anything just
yet. Usually, `StaticCollection` contains static data, specified when
collection is created. But because we haven't specified any data, collection
contains nothing.


To fix this problem, we have to configure a part of the collection responsible
for data production using its **settings**. Collection divides its internal
logic between a number of configurable *services*, and service that we need is
called **data** service. To modify it, we can pass a named argument called
`data_settings` to the collection's constructor:

```python
col = StaticCollection(
    "name", {},
    data_settings={"data": [1,2,3]}
)
```

Now try again iterating over the collection and now you'll see the result:

```python
for item in col:
    print(item)
```

It's not very impressive, but you didn't expect much from **static**
collection, right? There are other collections that are more smart, but we have
to learn more concepts of this extension to use them, so for now we'll only
take a brief look on them.

**Note**: collections have certain restrictions when it comes to amount of
data. By default, you'll see only around 10 records, even if you have more. The
same is true for `StaticCollection` - you can see it if you set `data`
attribute of its data-service to `range(1, 100)`. We'll learn how to control
these restrictions later.

`StaticCollection` works with static data. It can be used for tests or as a
placeholder for a collection that is not yet implemented. In rare cases it can
be used with arbitrary iterable to create a standard interface for data
interaction.

`ModelCollection` works with SQLAlchemy models. We are going to use two
attributes of its data-service: `model` and `is_scalar`. The former sets actual
model that collection processes, while the latter controls, how we work with
every individual record. By default, `ModelCollection` returns every record as
a number of columns, but we'll set `is_scalar=True` and receive model instance
for every record instead:

```python
col = ModelCollection(
    "", {},
    data_settings={"is_scalar": True, "model": model.User}
)

for user in col:
  assert isinstance(user, model.User)
  print(f"{user.name}, {user.email}")
```

`ApiSearchCollection` works with API actions similar to `package_search`. They
have to use `rows` and `start` parameters for pagination and their result must
contain `count` and `results` keys. Its data-service accepts `action` attribute
with the name of API action that produces the data:

```python
col = ApiSearchCollection(
    "", {},
    data_settings={"action": "package_search"}
)

for pkg in col:
  print(f"{pkg['id']}: {pkg['title']}")
```

`ApiListCollection` works with API actions similar to `package_list`. They have
to use `limit` and `offset` parameters for pagination and their result must be
represented by a list.

```python
col = ApiListCollection(
    "", {},
    data_settings={"action": "package_list"}
)

for name in col:
  print(name)
```

`ApiCollection` works with API actions similar to `user_list`. They have to
return all records at once, as list.

```python
col = ApiCollection(
    "", {},
    data_settings={"action": "user_list"}
)

for user in col:
  print(user["name"])
```


### Services

Collection itself contains just a bare minimum of logic, and all the
heavy-lifting is delegated to *services*. Collection knows how to initialize
services and usually the only difference between all your collections, is the
way all their services are configured.

Collection contains the following services:
* `data`: controls the exact data that can be received from
  collection. Contains logic for searching, filters, sorting, etc.
* `pager`: defines restrictions for data iteration. Exactly this service shows
  only 10 records when you iterating over static collection
* `serializer`: specifies how collection can be transformed into desired
  form. Using correct serializer you'll be able to dump the whole collection as
  CSV, JSON, YAML or render it as HTML table.
* `columns`: contains configuration of specific data columns used by other
  services. It may define model attributes that are dumped into CSV, names of
  the transformation functions that are applied to the certain attribute, names
  of the columns that are available for sorting in HTML representation of data.
* `filters`: contains configuration of additional widgets produced during data
  serialization. For example, when data is serialized into an HTML table,
  filters can define configuration of dropdowns and input fields from the data
  search form.

**Note**: You can define more services in custom collections. The list above
enumerates all the services that are available in the base collection and in
all collections shipped with the current extension. For example, one of
built-in collections, `DbCollection` has additional service called
`db_connection` that can communicate with DB.




#### Common logic

All services share a few common features. First of all, all services contain a
reference to the collection that uses/owns the service. Only one collection can
own the service. If you move service from one collection to another, you must
never use the old collection, that no longer owns the service. Depending on
internal implementation of the service, it may work without changes, but we
recommend removing such collections. At any point you can get the collection
that owns the service via `attached` attribute of the service:

```python
col = Collection("name", {})
assert col.data.attached is col
assert col.pager.attached is col
assert col.columns.attached is col

another_col = Collection(
    "another-name", {},
    data_instance=col.data
)
assert col.data.attached is not col
assert col.data.attached is another_col
assert col.data is another_col.data
```

Second common point of services is **settings**. Let's use `StaticData` for
tests. It has one configurable attribute(setting) - `data`. We can specify it
directly when creating data service instance: `StaticData(..., data=DATA)`. Or
we can specify it via `data_settings` when creating a collection:
`StaticCollection("name", {}, data_settings={"data": DATA})`. In both cases
`DATA` will be available as a `data` attribute of the data service. But it
doesn't mean that we can pass just any attribute in this way:

```python
data = StaticData(col, data=[], not_real=True)
assert hasattr(data, "data")
assert not hasattr(data, "not_real")
```

To allow overriding the value of attribute via settings, we have to define this
attribute as a **configurable attribute**. For this we need
`configurable_attribute` function from `ckanext.collection.shared`:

```python
class MyData(StaticData):
    i_am_real = configurable_attribute(False)

data = MyData(col, data=[], i_am_real=True)
assert hasattr(data, "data")
assert hasattr(data, "i_am_real")
assert data.i_am_real is True
```

`configurable_attribute` accepts either positional default value of the
attribute, or named `default_factory` function that generated default value
every time new instance of the service is created. `default_factory` must
accept a single argument - a new service that is instantiated at the moment:

```python
class MyData(StaticData):
    ref = 42
    i_am_real = shared.configurable_attribute(default_factory=lambda self: self.ref * 10)

data = MyData(col, data=[])
assert data.i_am_real == 420
```

Never use another configurable attributes in the `default_factory` - order in
which configurable attributes are initialized is not strictly defined. At the
moment of writing this manual, configurable attributes were initialized in
alphabetical order, but this implementation detail may change in future without
notice.

TODO: with_attributes
