from __future__ import annotations

import csv
import logging

from ckanext.collection import shared, types

from .base import Data

log = logging.getLogger(__name__)


class CsvData(Data[types.TData, types.TDataCollection]):
    source = shared.configurable_attribute()

    def compute_data(self):
        with open(self.source) as src:
            reader = csv.DictReader(src)
            return list(reader)
