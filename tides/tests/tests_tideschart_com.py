#!/bin/env python3
"""
Unit tests for tideschart_com.py

# NOTE:
# Not implementing a unit test for retrieve_tides_data() because it requires a Selenium browser object. Instead,
# it will be covered by an integration test.
"""


import json
import pytest
from datetime import datetime
from freezegun import freeze_time
from tideschart_com import TideschartDotCom


class Test_tideschart_com:

    @pytest.mark.xfail
    @pytest.mark.parametrize('file, exception', [
        ["bogus_input_URLs_1.json", ValueError],
        ["bogus_input_URLs_2.json", json.JSONDecodeError],
        ["bogus_input_URLs_3.json", ValueError]
    ])
    def test_retrieve_URLs_01(self, file, exception):
        test_obj = TideschartDotCom()
        with pytest.raises(exception):
            test_obj.retrieve_URLs(file)

    @pytest.mark.parametrize('file', [
        "sample_input_URLs_1.json",
        "sample_input_URLs_2.json",
    ])
    def test_retrieve_URLs_02(self, file):
        test_obj = TideschartDotCom()
        URLs = test_obj.retrieve_URLs(file)
        # Just a quick test of the first URL in each file. If the first URL changes, this test needs to change!!!!
        assert "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Salisbury" in URLs['URLs'][0]['URL']

    @pytest.mark.xfail
    @pytest.mark.parametrize('file, exception', [
        ["bogus_input_MUNIs_1.json", ValueError],
        ["bogus_input_MUNIs_2.json", ValueError],
    ])
    def test_retrieve_MUNIs_01(self, file, exception):
        test_obj = TideschartDotCom()
        with pytest.raises(exception):
            test_obj.retrieve_munis(file)

    @pytest.mark.parametrize('file', [
        "sample_input_munis_1.json",
        "sample_input_munis_2.json",
    ])
    def test_retrieve_MUNIs_02(self, file):
        test_obj = TideschartDotCom()
        MUNIs = test_obj.retrieve_munis(file)
        # Just a quick test of the first MUNI in each file. If the first MUNI changes, this test needs to change!!!!
        assert "Salisbury, MA" in MUNIs['MUNIs'][0]['MUNI']
        assert "United-States/Massachusetts/Essex-County/Salisbury/" in MUNIs['MUNIs'][0]['HINT']

    @freeze_time(datetime(2022, 9, 21))
    @pytest.mark.parametrize('data, expected', [
        ({'URL': 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm'},
         [datetime(2022, 9, 22, 9, 9), datetime(2022, 9, 22, 21, 17)]),
        ({'URL': 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm'},
         [datetime(2022, 9, 22, 9, 9, 0, 0)]),
    ])
    def test_parse_high_tide_data_01(self, data, expected):
        test_obj = TideschartDotCom()
        z = test_obj.parse_high_tide_data(data)
        assert z[0] == datetime(2022, 9, 22, 9, 9, 0)
