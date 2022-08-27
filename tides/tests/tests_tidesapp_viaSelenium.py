#!/bin/env python3
"""
tests_tidesapp_viaSelenium.py - Unit tests for tidesapp_viaSelenium
"""

import pytest
from datetime import datetime
from freezegun import freeze_time
from tidesapp_viaSelenium import TidesApp

class Tests_tidesapp_viaSelenium():

    @pytest.mark.xfail
    @pytest.mark.parametrize("filename", ['../tests/nosuchfile.json'])
    def test_load_user_locations_01(self, filename):
        app = TidesApp()
        with pytest.raises(FileNotFoundError):
            app.load_user_locations(filename)

    @pytest.mark.parametrize("filename", [''])
    def test_load_user_locations_02(self, filename):
        app = TidesApp()
        app.load_user_locations()


    @pytest.mark.parametrize("filename", ['../tests/sample_input.json'])
    def test_load_user_locations_03(self, filename):
        app = TidesApp()
        app.load_user_locations(filename)

    @pytest.mark.xfail
    @pytest.mark.parametrize("data", [
     'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41xx ▼ 1.64 ft ▲x5:57am ▼ 7:35pm',
    ])
    def test_parse_high_tide_data_01(self, data):
        app = TidesApp()
        with pytest.raises(ValueError):
            app.parse_high_tide_data(data)

    @freeze_time(datetime(2022, 8, 16))
    @pytest.mark.parametrize("data, expected", [
     ('Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm',
         [datetime(2022, 8, 22, 9, 9), datetime(2022, 8, 22, 21, 17)]),
     ('Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm',
         [datetime(2022, 8, 22, 9, 9)]),
    ])
    def test_parse_high_tide_data_02(self, data, expected):
        app = TidesApp()
        observed = app.parse_high_tide_data(data)
        assert observed == expected

    @freeze_time(datetime(2022, 8, 22))
    @pytest.mark.parametrize("data, expected", [
        ('Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm',
         [datetime(2022, 8, 22, 9, 9), datetime(2022, 8, 22, 21, 17)]),
        ('Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm',
         [datetime(2022, 8, 22, 9, 9)]),
        ])
    def test_parse_high_tide_data_03(self, data, expected):
        app = TidesApp()
        observed = app.parse_high_tide_data(data)
        assert observed == expected
