#!/bin/env python3
"""
MODULE: tests - A selection of pytest tests for the tidesapp app
"""

import pytest
from datetime import datetime
from datetime_utils import day2datetime
from freezegun import freeze_time

class Tests_datetime_utils():

    @freeze_time(datetime(2022, 1, 1))
    def test_datetime_utils_01(self):
        for i in range(1, 8):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 1 and d.day == i

    @freeze_time(datetime(2022, 6, 28))
    def test_datetime_utils_02(self):
        for i in range(28, 31):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 6 and d.day == i

    @freeze_time(datetime(2022, 6, 28))
    def test_datetime_utils_03(self):
        for i in range(1, 5):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 7 and d.day == i

    @freeze_time(datetime(2022, 12, 28))
    def test_datetime_utils_04(self):
        for i in range(1, 5):
            d = day2datetime(i)
            assert d.year == 2023 and d.month == 1 and d.day == i
