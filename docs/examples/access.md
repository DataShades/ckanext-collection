# Accessing data

This page contains examples of building collections using standard utilities
and reading data from such collections.

## Get records from the collection

/// admonition | Collection definition:

This example uses collection of numbers from 1 to 100

```python
from ckan import model
from ckanext.collection.shared import collection, data, pager

class Example(collection.Collection):
    DataFactory = data.StaticData.with_attributes(data=range(1, 100))

```
///

Collection itself is iterable, so you can access records using for-loop:

```python
col = Example()

for pkg in col:
    assert isinstance(pkg, int)

```

Or you can convert collection into a list:

```python
items = list(col)
```

When you iterate over collection, only current *page* of records is
yielded. The current page is controlled by pager service. Our example does not
configures pager, so we are using default values. Default pager shows the first
page, that contains 10 items from the data source.

```pycon
>>> len(items)
10
```

To change the page you can initialize a new instance of the collection and
modify pager settings

```pycon
>>> col = Example(pager_settings={"page": 3})
>>> list(col)
[21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
```

or you can replace pager service of the collection. To achieve it, initialize a
new pager instance, pass collection to its constructor as a first positional
argument, and specify pager settings as named arguments. You don't need to save
a new pager instance inside the collection properties. You don't need to store
pager instance inside any variable at all - when initialized, pager(and any
other service) is injected into collection automatically.

Collections use `pager.ClassicPager` by default, and that's what we'll use here

```pycon
>>> pager.ClassicPager(col, page=2)
>>> list(col)
[11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
```

If you want to modify size of the page, change value of `row_per_page` option
of the pager. In the following snippet we don't specify `page`, so it's set to `1`

```pycon
>>> pager.ClassicPager(col, rows_per_page=2)
>>> list(col)
[1, 2]
```

Instead of `pager.ClassicPager`, which relies on page number and page size, you
can use `pager.OffsetPager`, which is controlled by limit and offset. Results
are the same, only concept is different.

```pycon
>>> pager.OffsetPager(col, offset=14, limit=3)
>>> list(col)
[15, 16, 17]
```

If it's not enough, you can access data service of the collection directly as
`col.data`. Data service exposes two ways of accessing the records:

* data service itself is an iterable, that yields all available records
* data service has `range(start, end)` method that returns slice of all
  available items.

If you want to process all records in a loop, or transform them into a list,
data service is exactly what you need

```python
for item in col.data:
    ...

items = list(col.data)
```

Data service ignores the pager. No matter what page and page size are
configured, data service always returns all records when you transform it into
a list. Big data sources can consume a lot of memory in this case, so avoid
this transformation unless you are sure, your data sample is relatively small.

If you want to receive a slice of data source(and don't want to use
`pager.OffsetPager` which does exactly this thing), you can call
`col.data.range(start, end)`. To get 5 items starting from 10th:

```pycon
>>> list(col.data.range(10, 15))
[11, 12, 13, 14, 15]
```

`range` method of the data service is called by collection when it's used as
iterable. Collection gets position of the first and last elements from the
pager service and passes these parameters to `data.range`.

Implementation of `range` is provided by the data service. Some services
accepts only positive integers as start and end point. Other services may
accept negative offsets, float numbers or even dates. We are using `StaticData`
in this example, which transform `range` calls into slicing of the interal
data. I.e, as we are using squence of numbers as data, when `range(x, y)` is
called, internally it's transformed into `sequence[x:y]`.

It means, we can use negative indexes and `None` with the example collection

```pycon
>>> list(col.data.range(-5, None))
[95, 96, 97, 98, 99]
```

But other data services may not support this type of invocation. It's always a
good idea to check specification of the service, before using it.

## Get data from DB using SQLAlchemy model

/// admonition | Collection definition:

This example uses collection of all packages from the DB

```python
from ckan import model
from ckanext.collection.shared import collection, data

class Example(collection.Collection):
    DataFactory = data.ModelData.with_attributes(model=model.Package)
```
///

When you want fetch data from DB using a single model(something similar to
`model.Session.query(MODEL)`), using `data.ModelData` is often the simplest
option.

This service has one mandatory option - `model`. `data.ModelData` pulls all
records of the specified model from the DB and, by default, returns tuple-like
representation of each record.

```pycon
>>> col = Example()
>>> list(col)[0]
('id-123', 'name', 'title')
```

If you prefer working with model instances(`model.Package` in our example),
enable `is_scalar` option of the `data.ModelData` service.

```pycon
>>> col = Example(data_settings={"is_scalar": True})
>>> list(col)[0]
<Package id=123 name=hehe>
```

To filter records, specify `static_filters` option of the collection. It
accepts a collection of conditions that can be used with
`Query.filter`/`Select.where` methods of SQLAlchemy.

All datasets with `type=dataset` that were crated during last 30 days are
described by this collection:

```python
from datetime import date, timedelta

filter_type = model.Package.type == "dataset"
filter_date = model.Package.metadata_created > date.today() - timedelta(days=30)

col = Example(
    data_settings={
        "is_scalar": True,
        "static_filters": [filter_type, filter_date],
    },
)

for item in col:
    assert item.type == "dataset"
    assert date.today() - item.metadata_created < timedelta(days=30)

```

## Get data from API using package_search-like action

/// admonition | Collection definition:

This example uses collection of all packages from search API

```python
from ckan import model
from ckanext.collection.shared import collection, data

class Example(collection.Collection):
    DataFactory = data.ApiSearchData.with_attributes(action="package_search")
```
///

Any action that accepts `start` and `rows` parameters and returns result as
dictionary with `count` and `results` items, can be used with
`data.ApiSearchData`.

This service automatically moves through results when you iterate over
data. And you can loop through data service and process all the items:

```python
col = Example()

for item in col.data:
    ...
```

If you are working with `package_search` action directly, you have to write an
additional loop that moves offset further and fetches new portion of datasets:

```python
start = 0
search = tk.get_action("package_search")

while True:
    resp = search({}, {"start": start})["results"]

    if not results:
        break

    for item in results:
        ...

    start += len(results)
```

And with `data.ApiSearchData` this happens behind the scene and you just access
all the items using iteration over data service.

To set the `user` for the context, or enable `ignore_auth` flag, pass
corresponding options to the data service:

```python
col = Example(data_settings={
    "user": "custom-user",
    "ignore_auth": True,
})
```

And if you want to override search parameters or set the number of items
processed at once, use `payload` option of `data.ApiSearchData`.

```python
col = Example(data_settings={
    "payload": {
        "q": "test",
        "fq": "field:value",
        "rows": 100,
    },
})
```


## Get data from DB using arbitrary select statement

/// admonition | Collection definition:

This example uses collection of all packages from search API

```python
import sqlalchemy as sa

from ckan import model
from ckanext.collection.shared import collection, data

class Example(collection.Collection):
    DataFactory = data.StatementSaData
```
///

`data.StatementSaData` is a low-level version of `data.ModelData`. Instead of
working with SQLAlchemy model, it accepts any SQL
statement(`sqlalchemy.select`) and returns all records from it.

Select statement is controlled by `statement` option of the service.

```pycon
>>> col = Example(data_settings={
>>>     "statement": sa.select(model.User.name, model.User.sysadmin).where(
>>>         model.User.email.endswith("gmail.com"),
>>>     ),
>>> })
>>> list(col)
[('first-user', False), ('second-user', True)]
```

Records returned as tuple-like object by default. If you select only one
column, you still have to work with tuple-like object that contains a single
item. To make your life easier, consider enabling `is_scalar` flag, to return
only first column from every row of the data source.

```pycon
>>> col = Example(data_settings={
>>>     "statement": sa.select(model.User.name, model.User.sysadmin).where(
>>>         model.User.email.endswith("gmail.com"),
>>>     ),
>>>     "is_scalar": True
>>> })
>>> list(col)
['first-user', 'second-user']
```

Select statement has no restrictions regarding its size or complexity. If
required, use joins, group-by/having, subqueries, CTE, etc.

For example, a bit more complex collection that shows users and resources
inside packages created by them.

```python
col = Example(data_settings={
    "statement": sa.select(
        model.User.name,
        sa.func.count(model.Resource.id).label("res_number"),
        sa.func.array_agg(model.Package.name.distinct()).label("packages"),
        sa.func.array_agg(model.Resource.id).label("resources"),
    ).join(
        model.Package, model.Package.creator_user_id == model.User.id,
    ).join(
        model.Resource, model.Package.id == model.Resource.package_id
    ).group_by(model.User.id)
})
```

```pycon
>>> list(col)
[('default', 2, ['dataset1'], ['123', '456']),
 ('another-user', 1, ['dataset2'], ['888-888'])]

```
