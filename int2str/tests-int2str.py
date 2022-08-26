#!/bin/env python3
"""
Unit tests for the int2str module
"""

import pytest
from int2str import int2str, Int2strLang

class Tests_int2str():
    """
    Unit tests for the int2str module

    tests 0n - expected failures
    tests 1n - integers from -999 to 999
    tests 2n - integers less than -999 or greater than 999

    This is white-box testing. Tests 1n and 2n are separated because the 1n
    tests require only a single call to __int2str_util__(), while the 2n tests
    result in multiple calls to __int2str_util__().
    """

    @pytest.mark.xfail
    def test01(self):
        with pytest.raises(ValueError):
            int2str('bogus')

    @pytest.mark.xfail
    def test02(self):
        with pytest.raises(ValueError):
            int2str(99999999999999999999999)

    @pytest.mark.xfail
    def test03(self):
        with pytest.raises(ValueError):
            int2str(3.14159)

    @pytest.mark.xfail
    def test04(self):
        with pytest.raises(ValueError):
            int2str('bogus')

    def test11(self):
        assert int2str(0) == 'zero'
        assert int2str(-0) == 'zero'

    @pytest.mark.parametrize("n, expected", [
     (0, 'zero'),
     (1, 'one'),
     (2, 'two'),
     (3, 'three'),
     (4, 'four'),
     (5, 'five'),
     (6, 'six'),
     (7, 'seven'),
     (8, 'eight'),
     (9, 'nine'),
     (10, 'ten'),
     (11, 'eleven'),
     (12, 'twelve'),
     (13, 'thirteen'),
     (14, 'fourteen'),
     (15, 'fifteen'),
     (16, 'sixteen'),
     (17, 'seventeen'),
     (18, 'eighteen'),
     (19, 'nineteen'),
    ])
    def test12(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (-1,  'negative one'),
     (-2,  'negative two'),
     (-3,  'negative three'),
     (-4,  'negative four'),
     (-5,  'negative five'),
     (-6,  'negative six'),
     (-7,  'negative seven'),
     (-8,  'negative eight'),
     (-9,  'negative nine'),
     (-10, 'negative ten'),
     (-11, 'negative eleven'),
     (-12, 'negative twelve'),
     (-13, 'negative thirteen'),
     (-14, 'negative fourteen'),
     (-15, 'negative fifteen'),
     (-16, 'negative sixteen'),
     (-17, 'negative seventeen'),
     (-18, 'negative eighteen'),
     (-19, 'negative nineteen'),
    ])
    def test13(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (20, 'twenty'),
     (30, 'thirty'),
     (40, 'forty'),
     (50, 'fifty'),
     (60, 'sixty'),
     (70, 'seventy'),
     (80, 'eighty'),
     (90, 'ninety'),
    ])
    def test14(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (-20, 'negative twenty'),
     (-30, 'negative thirty'),
     (-40, 'negative forty'),
     (-50, 'negative fifty'),
     (-60, 'negative sixty'),
     (-70, 'negative seventy'),
     (-80, 'negative eighty'),
     (-90, 'negative ninety'),
    ])
    def test15(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (23, 'twenty three'),
     (34, 'thirty four'),
     (45, 'forty five'),
     (56, 'fifty six'),
     (67, 'sixty seven'),
     (78, 'seventy eight'),
     (89, 'eighty nine'),
     (99, 'ninety nine'),
    ])
    def test16(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (123, 'one hundred twenty three'),
     (234, 'two hundred thirty four'),
     (345, 'three hundred forty five'),
     (456, 'four hundred fifty six'),
     (567, 'five hundred sixty seven'),
     (678, 'six hundred seventy eight'),
     (789, 'seven hundred eighty nine'),
     (899, 'eight hundred ninety nine'),
     (987, 'nine hundred eighty seven'),
    ])
    def test17(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (1123, 'one thousand one hundred twenty three'),
     (6234, 'six thousand two hundred thirty four'),
     (20345, 'twenty thousand three hundred forty five'),
     (71456, 'seventy one thousand four hundred fifty six'),
     (333567, 'three hundred thirty three thousand five hundred sixty seven'),
     (888678, 'eight hundred eighty eight thousand six hundred seventy eight'),
     (999999, 'nine hundred ninety nine thousand nine hundred ninety nine'),
    ])
    def test20(self, n, expected):
        assert int2str(n) == expected

    @pytest.mark.parametrize("n, expected", [
     (1111123, 'one million one hundred eleven thousand one hundred twenty three'),
     (2226234, 'two million two hundred twenty six thousand two hundred thirty four'),
     (33320345, 'thirty three million three hundred twenty thousand three hundred forty five'),
     (44471456, 'forty four million four hundred seventy one thousand four hundred fifty six'),
     (555333567, 'five hundred fifty five million three hundred thirty three thousand five hundred sixty seven'),
     (666888678, 'six hundred sixty six million eight hundred eighty eight thousand six hundred seventy eight'),
     (777999999, 'seven hundred seventy seven million nine hundred ninety nine thousand nine hundred ninety nine'),
    ])
    def test21(self, n, expected):
        assert int2str(n) == expected

