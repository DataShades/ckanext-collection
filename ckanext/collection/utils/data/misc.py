from __future__ import annotations

import csv
import logging

from ckanext.collection import internal, types

from .base import Data

log = logging.getLogger(__name__)


class CsvFileData(Data[types.TData, types.TDataCollection]):
    """Data source for CSV file.

    CSV file available at path specified by `source` attribute of the service
    is read into memory and its every row transformed into dictionary.

    Warning:
        Iteration and size measurement uses cached version of source's content.
        If `source` attribute was overriden or its content was modified after
        service initialization, call `refresh_data()` method
        of the service to reset the cache.

    Attributes:
        source: path to CSV source

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.CsvFileData,
        >>>     data_settings={"source": "/path/to/file.csv"},
        >>> )
        >>> list(col)
        [
            {"column_1": "value_1", "column_2": "value_2"},
            ...
        ]
        ```



    """

    source: str = internal.configurable_attribute()

    def compute_data(self):
        with open(self.source) as src:
            reader = csv.DictReader(src)
            return list(reader)
