from __future__ import annotations

import csv
import logging

from ckanext.collection import internal, types

from .base import Data

log = logging.getLogger(__name__)


class CsvFileData(Data[types.TData, types.TDataCollection]):
    source = internal.configurable_attribute()

    def compute_data(self):
        with open(self.source) as src:
            reader = csv.DictReader(src)
            return list(reader)
