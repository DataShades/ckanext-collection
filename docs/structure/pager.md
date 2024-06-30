# Pager

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
col = StaticCollection(
    "name", {},
    data_settings={"data": range(1, 100)},
    pager_settings={"page": 3, "rows_per_page": 6}
)
assert list(col) == [13, 14, 15, 16, 17, 18]
```

Pagination details are often passed with search parameters and have huge
implact on the required data frame. Because of it, if `pager_settings` are
missing, `ClassicPager` will look for settings inside collection
parameters(second argument of the collection constructor). But in this case,
pager will use only items that has `<collection name>:` prefix:

```python
col = StaticCollection(
    "xxx",
    {"xxx:page": 3, "xxx:rows_per_page": 6},
    data_settings={"data": range(1, 100)}
)
assert list(col) == [13, 14, 15, 16, 17, 18]

col = StaticCollection(
    "xxx",
    {"page": 3, "rows_per_page": 6},
    data_settings={"data": range(1, 100)}
)
assert list(col) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

```
