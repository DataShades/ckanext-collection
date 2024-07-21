# Pager

## Overview

Pager service sets the upper and lower bounds on data used by collection. When
collection is used in loops, it gets position of the first and last record from
the pager and passes these values to `range` method of the data service. The
result is iterated over.

Collection uses [ClassicPager](#collection.shared.pager.ClassicPager) by default. It
implements pagination using `page` and `rows_per_page` parameters. These
settings of the pager service are used to compute `pager.start` and `pager.end`.

Default value of the `rows_per_page` is 10, and `page` is set to `1`.

```pycon
>>> col = collection.Collection(
>>>     data_factory=data.StaticData,
>>>     data_settings={"data": range(1, 100)},
>>> )
>>> col.pager.start
0
>>> col.pager.end
10
>>> list(col)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

If `page` is passed to `pager_settings` of the collection, or directly to the
pager constructor, it modifies `start` and `end`.

```pycon
>>> pager.ClassicPager(col, page=3)
>>> col.pager.start
20
>>> col.pager.end
30
>>> list(col)
[21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
```

`rows_per_page` controls the max number of items for a single page.

```pycon
>>> col = collection.Collection(
>>>     data_factory=data.StaticData,
>>>     data_settings={"data": range(1, 100)},
>>>     pager_settings={"rows_per_page": 3, "page": 5},
>>> )
>>> col.pager.start
12
>>> col.pager.end
15
>>> list(col)
[13, 14, 15]
```


Pagination details are often mixed with data filters, so `ClassicPager`, used
by default in Collection, check if `page` and `rows_per_page` are available in
`params` of the collection. If so, these values are used instead of pager
settings.

/// admonition
    type: example

In this example collection have different pager settings specified by
`params`(second positional argument) and `pager_settings`. In such situation
`params` have higher priority and `pager_settings` are ignored.

```pycon
>>> col = collection.Collection(
>>>     "",
>>>     {"rows_per_page": 1, "page": 2}, # (1)!
>>>     data_factory=data.StaticData,
>>>     data_settings={"data": range(1, 100)},
>>>     pager_settings={"rows_per_page": 3, "page": 5},  # (2)!
>>> )
>>> col.pager.start
1
>>> col.pager.end
2
>>> list(col)
[2]
```

1. `params` have higher priority and will be used by collection when present
2. `pager_settings` are not used because they conflict with `params`
///

## Available pager factories

::: collection.shared.pager.Pager
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.pager.ClassicPager
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.pager.OffsetPager
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.pager.TemporalPager
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []
