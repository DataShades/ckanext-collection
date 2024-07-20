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
