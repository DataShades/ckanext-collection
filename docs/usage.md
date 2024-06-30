# Usage

## Register collection

Collection can be initialized anywhere in code

/// admonition
    type: example

```python
from my.module import MyCollection

col = MyCollection()

```
///

But it's recommended to register collections globally.

Collections are registered via [ICollection
interface](interfaces.md#icollection) or via CKAN signals. Registered
collection can be initialized anywhere in code using helper. It can also be
used in a number of generic endpoints that render collection as HTML or export
it into different formats.

/// tab | Register via interface
```python
import ckan.plugins as p
from ckanext.collection import shared

class MyPlugin(p.SingletonPlugin):
    p.implements(shared.ICollection, inherit=True)

    def get_collection_factories(
        self,
    ) -> dict[str, shared.types.CollectionFactory]:
        return {
            "my-collection": MyCollection,
        }

```
///

/// tab | Register via signal

```python
import ckan.plugins as p

class MyPlugin(p.SingletonPlugin):
    p.implements(p.ISignal)

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.ckanext.signal("collection:register_collections"): [
                get_collection_factories,
            ],
        }

def get_collection_factories(sender: None): # (1)!
    return {
        "my-collection": MyCollection,
    }

```

1. Signal listerners must receive at least one argument containing the sender
   of the signal. Signal that register collections always sets `None` as a
   sender.

///


`get_collection_factories` returns a dictionary with collection names(letters,
digits, underscores and hyphens are allowed) as keys, and collection factories
as values. In most generic case, collection factory is just a collection's
class itself. But you can use any function with signature `(str, dict[str,
Any], **Any) -> Collection` as a factory.

/// admonition
    type: example

The following function is a valid collection factory and it can be returned
from `get_collection_factories`

```python
def my_factory(name: str, params: dict[str, Any], **kwargs: Any):
    """Collection that shows 100 numbers per page"""
    params.setdefault("rows_per_page", 100)
    return MyCollection(name, params, **kwargs)
```
///

## Initialize collection

Collection class defines the data source of collection and different aspects of
it behavior. But collection class itself does not contain any data and
collection instance must be created to work with data.

Any collection can be initialized directly, using collection class. And every
[registered collection](#register-collection) can be initialized via
`get_collection` function. Arguments are the same in both cases. Collection
requires the name, parameters and accepts arbitrary number of keyword-only
arguments, that are passed to underlying services.

/// tab | Initialize registered collection
```python
col = get_collection(
    "my-collection",
    {},
    pager_settings={"rows_per_page": 100}
)
```
/// tip

Second argument of `get_collection` expects parameters prefixed by collection
name. In example above, to choose the second page, you need to pass
`{"my-collection:page": 2}` as parameters.

If you are using unprefixed parameters, like `{"page": 2}` and don't want to
adapt them to expected form, pass `True` as the third argument to
`get_collection`, and every key inside parameters will get required prefix
automatically.

```python
col = get_collection(
    "my-collection",
    {"page": 2},
    True,
    pager_settings={"rows_per_page": 100}
)
```
///
///

/// tab | Initialize collection using class
```python
col = MyCollection(
    "",
    {},
    pager_settings={"rows_per_page": 100},
)
```
///

## Use collection data

/// tip

If you want to try examples below, but you haven't defined any collection yet,
you can use the following definition for collection of numbers from 1 to 25:

```python
from ckanext.collection.shared import collection, data
class MyCollection(collection.Collection):
    DataFactory = data.StaticData.with_attributes(data=[
        {"number": num, "index": idx}
        for idx, num in enumerate(range(1,26))
    ])

```
///

Intended way to access the data is iteration over collection instance. In this
way, you access only specific chunk of data, limited by collection's pager.

```pycon
>>> col = MyCollection()
>>> list(col)
[{'number': 1, 'index': 0},
 {'number': 2, 'index': 1},
 {'number': 3, 'index': 2},
 {'number': 4, 'index': 3},
 {'number': 5, 'index': 4},
 {'number': 6, 'index': 5},
 {'number': 7, 'index': 6},
 {'number': 8, 'index': 7},
 {'number': 9, 'index': 8},
 {'number': 10, 'index': 9}]
```

Different page can be accessed by passing `page` inside params to collection's
constructor

```pycon
>>> col = MyCollection("", {"page": 3}) # (1)!
>>> list(col)
[{'number': 21, 'index': 20},
 {'number': 22, 'index': 21},
 {'number': 23, 'index': 22},
 {'number': 24, 'index': 23},
 {'number': 25, 'index': 24}]
```

1. More idiomatic form of this initialization is `#!py3
   MyCollection(pager_settings={"page": 3}))`. But this form is longer an
   required deeper knowledge of collections.

If you need to iterate over all collection items, without pagination, you can
use `data` attribute of the collection.

/// warning

Using data directly can result in enormous memory consumption. Avoid
transforming data into list(`#!py3 list(col.data)`) or processing it as single object
in any other way. Instead, iterate over collection items using loops or similar
tools.

///

/// admonition
    type: example

```pycon
>>> sum = 0
>>> for item in col.data:
>>>     sum += item["number"]
>>>
>>> print(sum)
325
```
///

## Serialize collection

The ultimate goal of every collection is serialization. It may be serialization
as HTML to show collection on one of application web-pages. Or serialization as
JSON to send collection to the external API. Or serialization as CSV to allow
user downloading the collection. Or even serialization as pandas' DataFrame to
process data from the collection using more advanced tools.

`serializer` service of collection is responsible for serialization. If
required format of collections output is known in advance, `SerializerFactory`
can be defined on collection level.

If the format of serialization can vary, `serializer` can be initialized
separately.

/// tab | Using SerializerFactory

```python
from ckanext.collection.shared import collection, serialize, data

class MyCollection(collection.Collection):
    DataFactory = data.StaticData.with_attributes(data=[
        {"number": num, "index": idx}
        for idx, num in enumerate(range(1,26))
    ])
    SerializerFactory = serialize.CsvSerializer

col = MyCollection()
print(col.serializer.serialize())
```
///
/// tab | Creating serializers on demand

```python
from ckanext.collection.shared import collection, serialize, data

class MyCollection(collection.Collection):
    DataFactory = data.StaticData.with_attributes(data=[
        {"number": num, "index": idx}
        for idx, num in enumerate(range(1,26))
    ])


col = MyCollection()

json = serialize.JsonSerializer(col)
print(json.serialize())

csv = serialize.CsvSerializer(col)
print(csv.serialize())

```
///


/// admonition
    type: warning


Keep in mind, as any other collection's service, serializer attaches itself to
collection when initialized and replaces the previous serializer.

```pycon
>>> col = MyCollection()
>>> isinstance(col.serializer, serialize.Serializer)
True
>>> serialize.JsonSerializer(col)
>>> isinstance(col.serializer, serialize.JsonSerializer)
True
>>> serialize.CsvSerializer(col)
>>> isinstance(col.serializer, serialize.CsvSerializer)
True
```
///
