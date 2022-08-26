#!/bin/env python3
"""
tests_datetime_utils - Unit tests for tideapp's datetime utilities
"""

import pytest
from datetime import datetime
from freezegun import freeze_time
from datetime_utils import day2datetime

class Tests_datetime_utils():

    """
    Each test uses freeze_time (from the freezegun pytest plugin) to cause the
    test to operate in the context of the frozen time. This provides persistent
    test consistency (i.e., you'll get the same results if you run this unit test
    on Monday, Saturday, August 16th, December 31st or the 29th of February)

    In each test, the variable 'i' represents a day-of-month, and is relative to
    the datetime set by freeze_time. The tests loop through several values of 'i'
    to assert that the called function operates properly in various scenarios.
    """

    @freeze_time(datetime(2022, 1, 1))
    def test_datetime_utils_01(self):
        """No overflow. Start of month."""
        for i in range(1, 8):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 1 and d.day == i

    @freeze_time(datetime(2022, 6, 28))
    def test_datetime_utils_02(self):
        """No overflow. End of month."""
        for i in range(28, 31):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 6 and d.day == i

    @freeze_time(datetime(2022, 6, 28))
    def test_datetime_utils_03(self):
        """Month overflow."""
        for i in range(1, 5):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 7 and d.day == i

    @freeze_time(datetime(2022, 12, 28))
    def test_datetime_utils_04(self):
        """Month and year overflow."""
        for i in range(1, 5):
            d = day2datetime(i)
            assert d.year == 2023 and d.month == 1 and d.day == i
