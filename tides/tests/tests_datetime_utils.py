#!/bin/env python3
"""
Unit tests for tideapp's datetime utilities
"""

import pytest
from datetime import datetime
from freezegun import freeze_time
from datetime_utils import day2datetime, timestr2time


class Tests_datetime_utils:

    """
    Each test uses freeze_time (from the freezegun pytest plugin) to
    cause the test to operate in the context of the frozen time. This
    provides persistent test consistency (i.e., you'll get the same
    results if you run this unit test on Monday, Saturday, August
    16th, December 31st or the 29th of February)

    In each test, the variable 'i' represents a day-of-month, and
    is relative to the datetime set by freeze_time. The tests loop
    through several values of 'i' to assert that the called function
    operates properly in various scenarios.
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

    @freeze_time(datetime(2022, 8, 22))
    def test_datetime_utils_04(self):
        """No overflow. Normal date"""
        for i in range(22, 28):
            d = day2datetime(i)
            assert d.year == 2022 and d.month == 8 and d.day == i

    @freeze_time(datetime(2022, 12, 28))
    def test_datetime_utils_05(self):
        """Month and year overflow."""
        for i in range(1, 5):
            d = day2datetime(i)
            assert d.year == 2023 and d.month == 1 and d.day == i

    @pytest.mark.parametrize("timestr, hour, minute", [
        ('1:00am', 1, 0),
        ('1:00pm', 13, 0),
        ('01:22pm', 1, 22),
        ('2:34am', 2, 34),
        ('2:34 am', 2, 34),
        ('3:45 pm', 15, 45),
        ('11:59 pm', 23, 59),
    ])
    def test_timestr2time_01(self, timestr, hour, minute):
        t = timestr2time(timestr)
        assert t.hour == hour and t.minute == minute

    @pytest.mark.xfail
    @pytest.mark.parametrize("timestr", [
        '0:00am',
        '0:00pm',
        '12:60 am',
        '24:34 am',
        '24:34 pm',
    ])
    def test_timestr2time_01(self, timestr):
        with pytest.raises(ValueError):
            timestr2time(timestr)
