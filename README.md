[![Tests](https://github.com/DataShades/ckanext-collection/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-collection/actions)

# ckanext-collection

Tools for building interfaces for data collections.

This extension simplifies describing series of items, such as datasets from
search page, users registered on portal, rows of CSV file, tables in DB,
etc. Once you defined the way items are obtained from data source, you'll get
generic interface for pagination, search and displaying data in any format:
HTML page, CSV document, JSON list, or any other custom format that you can
describe.

Read the [documentation](https://datashades.github.io/ckanext-collection/) for
a full user guide.


## Quickstart

Install the extension

```sh
pip install ckanext-collection
```

Add `collection` to the `ckan.plugins` setting in your CKAN config file

Define the collection

```python

from ckan import model
from ckanext.collection.utils import *


## collection of all resources
class MyCollection(Collection):
    DataFactory = ModelData.with_attributes(model=model.Resource)
    # `names` controls names of fields exported by serializer
    # further in this guide
    ColumnsFactory = cu.Columns.with_attributes(names=["name", "size"])

## collection of all packages available via search API
class MyCollection(Collection):
    DataFactory = ApiSearchData.with_attributes(action="package_search")
    ColumnsFactory = cu.Columns.with_attributes(names=["name", "title"])

## collection of all records from CSV file
class MyCollection(Collection):
    DataFactory = CsvData.with_attributes(source="/path/to/file.csv")
    ColumnsFactory = cu.Columns.with_attributes(names=["a", "b"])

```

Initialize collection object and work with data:

```python

# collection with first page of results(1st-10th items)
col = MyCollection("", {})
items = list(col)

# collection with third page of results(21st-30th items)
col = MyCollection("", {"page": 3})
items = list(col)


# alternatively, read all the items into memory at once, without pagination.
# It may be quite expensive operation depending on number of items
col = MyCollection("", {})
items = list(col.data)

# or get the slice of data from 2nd till 5th(not includeing 5th,
# just like in python slices)
items = col.data.range(2, 5)

# check total number of items in collection
print(col.data.total)

```

Serialize data using `Serializer` service:

```python

# serialize into JSON string
serializer = JsonSerializer(col)

# or serialize into CSV string
serializer = CsvSerializer(col)

# or serialize into list of dictionaries
serializer = DictListSerializer(col)


print(serializer.serialize())

```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
