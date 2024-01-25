[![Tests](https://github.com/DataShades/ckanext-collection/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-collection/actions)

# ckanext-collection

Base classes for viewing data series from CKAN.

## Content

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
  * [Overview](#overview)
  * [Services](#services)
    * [Common logic](#common-logic)
    * [Data service](#data-service)
    * [Pager service](#pager-service)
    * [Serializer service](#serializer-service)
    * [Columns service](#columns-service)
    * [Filters service](#filters-service)
* [Config settings](#config-settings)
* [License](#license)

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| master       | yes         |

## Installation

To install ckanext-collection:

1. Install the extension:
   ```sh
   pip install ckanext-collection
   ```

1. Add `collection` to the `ckan.plugins` setting in your CKAN
   config file .

## Usage

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
for data production using **settings**. Collection divides its internal logic
between a number of *services*, and service that we need is called **data**
service. To modify it, we can pass a named argument called `data_settings` to
the collection's constructor:

```python
col = StaticCollection("name", {}, data_settings={"data": [1,2,3]})
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
a number of columns, but we'll set its value to `True` and receive model
instance for every record instead:

```python
col = ModelCollection("", {}, data_settings={"is_scalar": True, "model": model.User})
for user in col:
  assert isinstance(user, model.User)
  print(f"{user.name}, {user.email}")
```

`ApiSearchCollection` works with API actions similar to `package_search`. They
have to use `rows` and `start` parameters for pagination and their result must
contain `count` and `results` keys. Its data-service accepts `action` attribute
with the name of API action that produces the data:

```python
col = ApiSearchCollection("", {}, data_settings={"action": "package_search"})
for pkg in col:
  print(f"{pkg['id']}: {pkg['title']}")
```

`ApiListCollection` works with API actions similar to `package_list`. They have
to use `limit` and `offset` parameters for pagination and their result must be
represented by a list.

```python
col = ApiListCollection("", {}, data_settings={"action": "package_list"})
for name in col:
  print(name)
```

`ApiCollection` works with API actions similar to `user_list`. They have to
return all records at once, as list.

```python
col = ApiCollection("", {}, data_settings={"action": "user_list"})
for user in col:
  print(user["name"])
```

### Collection intialization

Collection constructor has two mandatory arguments: name and parameters.

Name is used as collection identifier and it's better to keep this value unique
accross collections. For example, name is used for computing HTML table `id`
attribute when serializing collection as an HTML table. If you render two
collections with the same name, you'll get two identical IDs on the page.

Params are usually used by data and pager service for searching, sorting,
etc. Collection does not keep all the params. Instead, it stores only items
with key prefixed by `<name>:`. I.e, if collection has name `hello`, and you
pass `{"hello:a": 1, "b": 2, "world:c": 3}`, collection will remove `b` and
`world:c` members. As for `hello:a`, collection strips `<name>:` prefix from
it. So, in the end, collection stores `{"a": 1}`.  You can check params of the
collection using `params` attribute:

```python
col = Collection("hello", {"hello:a": 1, "b": 2, "world:c": 3})
assert col.params == {"a": 1}

col = Collection("world", {"hello:a": 1, "b": 2, "world:c": 3})
assert col.params == {"c": 3}
```

It allows you rendering and processing multiple collections simultaneously on
the same page. Imagine that you have collection `users` and collection
`packages`. You want to see second page of `users` and fifth of
`packages`. Submit the query string `?users:page=2&packages:page=5` and
initialize collections using the following code:

```python
from ckan.logic import parse_params
from ckan.plugins import toolkit as tk

params = parse_params(tk.request.args)

users = ModelCollection("users", params, data_settings={"model": model.User})
packages = ModelCollection("packages", params, data_settings={"model": model.Package})

assert users.pager.page == 2
assert packages.pager.page == 5
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

**Note**: You can define more services in custom collections. The list above enumerates
all the services that are available in the base collection and in all
collections shipped with the current extension.


When a collection is created, it creates an instance of each service using
service factories and service settings. Base collection and all collections
that extend it already have all details for initializing every service:

```python
col = Collection("name", {})
print(f"""{col.data=},
{col.pager=},
{col.serializer=},
{col.columns=},
{col.filters=}""")

assert list(col) == []
```

This collection has no data. We can initialize an instance of `StaticData` and
replace the data service of the collection with it. Every service has one
required argument: collection that will use the service. All other arguments
are used as a service settings and must be passed by name. Remember, all the
classes used in this manual are available inside `ckanext.collection.utils`:

```python
static_data = StaticData(col, data=[1,2,3])
col.replace_service(static_data)

assert list(col) == [1, 2, 3]
```

Look at `Colletion.replace_service`. It accepts only service instance. There is
no need to pass the name of the service that must be replaced - collection can
understand it without help. And pay attention to the first argument of service
constructor. It must be the collection that is going to use the service. Some
services may work even if you pass a random value as the first argument, but
it's an exceptional situation and one shouldn't rely on it.

If existing collection is no longer and you are going to create a new one, you
probably want to reuse a service from an existing collection. Just to avoid
creating the service and calling `Collection.replace_service`, which will save
you two lines of code. In this case, use `<service>_instance` parameter of the
collection constructor:

```python
another_col = Collection("another-name", {}, data_instance=col.data)
assert list(another_col) == [1, 2, 3]
```

If you do such thing, make sure you are not using old collection anymore. You
just transfered one of its services to another collection, so there is no
guarantees it will function properly. If you want to use a custom factory for
the service, instead of transfering a service instance, it's better to
customize service factory. You can tell which class to use for making an
instance of a service using `<service>_factory` parameter of the collection
contstructor:

```python
col = Collection("name", {}, data_factory=StaticData)
assert list(col) == []
```

But in this way we cannot specify the `data` attribute of the `data` factory!
No worries, there are multiple ways to overcome this problem. First of all, all
the settings of the service are available as its attributes. It means that
`data` setting is the same as `data` attribute of the service. If you can do
`StaticData(..., data=...)`, you can as well do `service = StaticData(...);
service.data = ...`:

```python
col = Collection("name", {}, data_factory=StaticData)
col.data.data = [1, 2, 3]
assert list(col) == [1, 2, 3]
```

But there is a better way. You can pass `<service>_settings` dictionary to the
collection constructor and it will be passed down into corresponding service
factory:

```python
col = Collection("name", {}, data_factory=StaticData, data_settings={"data": [1, 2, 3]})
assert list(col) == [1, 2, 3]
```


It works well for individual scenarios, but when you are creating a lot of
collections with the static data, you want to omit some standard parameters. In
this case you should define a new class that extends Collection and declares
`<Service>Factory` attribute:

```python
class MyCollection(Collection):
    DataFactory = StaticData

col = MyCollection("name", {}, data_settings={"data": [1, 2, 3]})
assert list(col) == [1, 2, 3]
```

You still can pass `data_factory` into `MyCollection` constructor to override
data service factory. But now, by default, `StaticData` is used when it's not
specified explicitly.

Finally, if you want to create a subclass of service, that has a specific value
of certain attributes, i.e something like this:

```python
class OneTwoThreeData(StaticData):
    data = [1, 2, 3]
```

you can use `Service.with_attributes(attr_name=attr_value)` factory method. It
produce a new service class(factory) with specified attributes bound to a
static value. For example, that's how we can define a collection, that always
contains `[1, 2, 3]`:

```python
class MyCollection(Collection):
    DataFactory = StaticData.with_attributes(data=[1, 2, 3])

col = MyCollection("name", {})
assert list(col) == [1, 2, 3]
```

Now you don't have to specify `data_factory` or `data_settings` when creating a
collection. It will always use `StaticData` with `data` set to `[1, 2, 3]`
. Make sure you mean it, because now you cannot override the data using
`data_settings`.


#### Common logic

All services share a few common features. First of all, all services contain a
reference to the collection that users/owns the service. Only one collection
can own the service. If you move service from one collection to another, you
must never use the old collection, that no longer owns the service. Depending
on internal implementation of the service, it may work without changes, but we
recommend removing such collections. At any point you can get the collection
that owns the service via `attached` attribute of the service:

```python
col = Collection("name", {})
assert col.data.attached is col
assert col.pager.attached is col
assert col.columns.attached is col

another_col = Collection("another-name", {}, data_instance=col.data)
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
    i_am_real = configurable_attribute(default_factory=lambda self: self.ref * 10)

data = MyData(col, data=[])
assert data.i_am_real == 420
```

Never use another configurable attributes in the `default_factory` - order in
which configurable attributes are initialized is not strictly defined. At the
moment of writing this manual, configurable attributes were initialized in
alphabetical order. But this implementation detail may change in future without
notice.

#### Data service

This service produces the data for collection. Every data service must:

* be Iterable and iterate over all available records by default
* define `total` property, that reflects number of available records so that
  `len(list(data)) == data.total`
* define `range(start: Any, end: Any)` method that returns slice of the data

Base class for data services - `Data` - already contains a simple version of
this logic. You have to define only one methods to make you custom
implementations: `compute_data()`. When data if accessed for the first time,
`compute_data` is called. Its result cached and used for iteration in
for-loops, slicing via `range` method and size measurement via `total`
property.

```python
class CustomData(Data):
    def compute_data(self) -> Any:
        return "abcdefghijklmnopqrstuvwxyz"

col = Collection("name", {}, data_factory=CustomData)
assert list(col) == ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
assert col.data.total == 26
assert col.data.range(-3, None) == "xyz"

```

If you need more complex data source, make sure you defined `__iter__`, `total`, and `range`:

```python
class CustomData(Data):
    names = configurable_attribute(default_factory=["Anna", "Henry", "Mary"])

    @property
    def total(self):
        return len(self.names)

    def __iter__(self):
        yield from self.names

    def range(self, start: Any, end: Any):
        if not isinstance(start, str) or not isinstance(end, str):
            return []

        for name in names:
            if name < start:
                continue
            if name > end:
                break
            yield name
        yield from range(start, end)

```


#### Pager service

Pager service sets the upper and lower bounds on data used by
collection. Default pager used by collection relies on numeric `start`/`end`
values. But it's possible to define custom pager that uses alphabetical or
temporal bounds, as long as `range` method of your custom data service supports
these bounds.

Standard pager(`ClassicPager`) has two configurable attributes: `page`(default:
1) and `rows_per_page`(default: 10).

```python
col = StaticCollection("name", {})
assert col.pager.page == 1
assert col.pager.rows_per_page == 10
```

Because of these values you see only first 10 records from data when iterating
the collection. Let's change pager settings:

```python
col = StaticCollection("name", {}, data_settings={"data": range(1, 100)}, pager_settings={"page": 3, "rows_per_page": 6})
assert list(col) == [13, 14, 15, 16, 17, 18]
```

Pagination details are often passed with search parameters and have huge
implact on the required data frame. Because of it, if `pager_settings` are
missing, `ClassicPager` will look for settings inside collection
parameters(second argument of the collection constructor). But in this case,
pager will use only items that has `<collection name>:` prefix:

```python
col = StaticCollection("xxx", {"xxx:page": 3, "xxx:rows_per_page": 6}, data_settings={"data": range(1, 100)})
assert list(col) == [13, 14, 15, 16, 17, 18]

col = StaticCollection("xxx", {"page": 3, "rows_per_page": 6}, data_settings={"data": range(1, 100)})
assert list(col) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

```

#### Serializer service

Serializer converts data into textual or binary representation. Serializers are
main users of columns service, because it contains details about specific data
columns. And serializers often iterate data service directly(ignoring `range`
method), to serialize all available records. The only required method for
serializer is `stream`. This method must return an iterable of `str` or `byte`
fragments of the serialized data. And there must be at least one fragment. Even
if there is no data, serializer must return at least `''` or `b'` from
`stream`.

```python
class NewLineSerializer(Serializer):
    def stream(self):
        for item in self.attached.data:
            yield str(item) + "\n"

col = StaticCollection(
    "name", {},
    serializer_factory=NewLineSerializer,
    data_settings={"data": [1, 2, 3]}
)
assert "".join(col.serializer.stream()) == "1\n2\n3\n"
```

Serializer also has `render` method, that combines all fragments from `stream`
into a single sequence:

```python
assert col.serializer.render() == "1\n2\n3\n"
```

Use `render` only when you are sure that you have enough memory for all the
serialized records. In most cases it will be wiser to send streaming response
to client using `stream` generator.

#### Columns service

This service contains additional information about separate columns of data
records. It defines following settings:

* names: all available column names. Used by other settings of columns service
* hidden: columns that should not be shown by serializer. Used by serializer
  services
* visible: columns that must be shown by serializer. Used by serializer
  services
* sortable: columns that support sorting. Used by data services
* filterable: columns that support filtration/facetting. Used by data services
* searchable: columns that support search by partial match. Used by data
  services
* labels: human readable labels for columns. Used by serializer services


#### Filters service

This service used only by HTML table serializers at the moment. It has two
configurable attributes `static_filters` and `static_actions`. `static_filters`
are used for building search form for the data table. `static_actions` are not
used, but you can put into it details about batch or record-level actions and
use these details to extend one of standard serializers. For example,
ckanext-admin-panel defines allowed actions (remove, restore, hide) for content
and creates custom templates that are referring these actions.

## Config settings

```ini
# Names of registered collections that are viewable by any visitor, including
# anonymous.
# (optional, default: )
ckanext.collection.auth.anonymous_collections =

# Names of registered collections that are viewable by any authenticated
# user.
# (optional, default: )
ckanext.collection.auth.authenticated_collections =

# Add HTMX asset to pages. Enable this option if you are using CKAN v2.10
# (optional, default: false)
ckanext.collection.include_htmx_asset = false

# Initialize CKAN JS modules every time HTMX fetches HTML from the server.
# (optional, default: false)
ckanext.collection.htmx_init_modules = false

# Import path for serializer used by CSV export endpoint.
# (optional, default: ckanext.collection.utils.serialize:CsvSerializer)
ckanext.collection.export.csv.serializer = ckanext.collection.utils.serialize:CsvSerializer

# Import path for serializer used by JSON export endpoint.
# (optional, default: ckanext.collection.utils.serialize:JsonSerializer)
ckanext.collection.export.json.serializer = ckanext.collection.utils.serialize:JsonSerializer

# Import path for serializer used by JSONl export endpoint.
# (optional, default: ckanext.collection.utils.serialize:JsonlSerializer)
ckanext.collection.export.jsonl.serializer = ckanext.collection.utils.serialize:JsonlSerializer

# Import path for serializer used by `format`-export endpoint.
# (optional, default: )
ckanext.collection.export.<format>.serializer =

```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
