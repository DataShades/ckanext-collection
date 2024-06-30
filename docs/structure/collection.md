# Collection


Collection constructor has two mandatory arguments: name and parameters.

Name is used as collection identifier and it's better to keep this value unique
accross collections. For example, name is used for computing HTML table `id`
attribute when serializing collection as an HTML table. If you render two
collections with the same name, you'll get two identical IDs on the page.

Params are usually used by data and pager service for searching, sorting,
etc. Collection does not keep all the params. Instead, it stores only items
with key prefixed by `<name>:`. I.e, if collection has name `hello`, and you
pass `{"hello:a": 1, "b": 2, "world:c": 3}`, collection will remove `b`(because
it has no collection name plus colon prefix) and `world:c` members(because it
uses `world` instead of `hello` in prefix). As for `hello:a`, collection strips
`<name>:` prefix from it. So, in the end, collection stores `{"a": 1}`.  You
can check params of the collection using `params` attribute:

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

users = ModelCollection(
    "users", params,
    data_settings={"model": model.User}
)
packages = ModelCollection(
    "packages", params,
    data_settings={"model": model.Package}
)

assert users.pager.page == 2
assert packages.pager.page == 5
```

---

When a collection is created, it creates an instance of each service using
service factories and service settings. Base collection and all collections
that extend it already have all details for initializing every service:

```python
col = Collection("name", {})
print(f"""Services:
  {col.data=},
  {col.pager=},
  {col.serializer=},
  {col.columns=},
  {col.filters=}""")

assert list(col) == []
```

This collection has no data. We can initialize an instance of `StaticData` and
replace the existing data service of the collection with new `StaticData`
instance.

Every service has one required argument: collection that owns the service. All
other arguments are used as a service settings and must be passed by
name. Remember, all the classes used in this manual are available inside
`ckanext.collection.utils`:

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

If existing collection is no longer used and you are going to create a new one,
you sometimes want to reuse a service from an existing collection. Just to
avoid creating the service and calling `Collection.replace_service`, which will
save you two lines of code. In this case, use `<service>_instance` parameter of
the collection constructor:

```python
another_col = Collection("another-name", {}, data_instance=col.data)
assert list(another_col) == [1, 2, 3]
```

If you do such thing, make sure you are not using old collection anymore. You
just transfered one of its services to another collection, so there is no
guarantees that old collection with detached service will function properly.

It's usually better to customize service factory, instead of passing existing
customized instance of the service around. You can tell which class to use for
making an instance of a service using `<service>_factory` parameter of the
collection contstructor:

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

**Note**: `data` service caches its data. If you already accessed data property
from the `StaticData`, assigning an new value doesn't have any effect because
of the cache. You have to call `col.data.refresh_data()` after assigning to
rebuild the cache.

But there is a better way. You can pass `<service>_settings` dictionary to the
collection constructor and it will be passed down into corresponding service
factory:

```python
col = Collection(
    "name", {},
    data_factory=StaticData,
    data_settings={"data": [1, 2, 3]}
)
assert list(col) == [1, 2, 3]
```


It works well for individual scenarios, but when you are creating a lot of
collections with the static data, you want to omit some standard parameters. In
this case you should define a new class that extends Collection and declares
`<Service>Factory` attribute:

```python
class MyCollection(Collection):
    DataFactory = StaticData

col = MyCollection(
    "name", {},
    data_settings={"data": [1, 2, 3]}
)
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

---
