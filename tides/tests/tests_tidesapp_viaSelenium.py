#!/bin/env python3
"""
tests_tidesapp_viaSelentium.py - Unit tests for tidesapp 
"""

""" *** WORK-IN-PROGRESS *** """

import pytest
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

