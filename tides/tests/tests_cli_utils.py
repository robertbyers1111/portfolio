#!/bin/env python3
"""
Unit tests for tideapp's cli utility
"""

import pytest
import sys
import os
from cli_utils import process_command_line


class Tests_cli_utils:

    # It is a mess trying to test the cli with pytest because mocking sys.argv[1:] messes with pytest's command line

    @pytest.mark.xfail
    @pytest.mark.parametrize("mock_cli", [
        ['-h', SystemExit],
        ['--help', SystemExit],
    ])
    def test_cli_utils_01(self, mock_cli):
        sys.argv[1:] = mock_cli
        process_command_line()

    @pytest.mark.xfail
    # @pytest.mark.parametrize("mock_cli, expected_error", [
    # ])
    @pytest.mark.parametrize("mock_cli, expected_error", [
        [[''], ValueError],
        [['bogus.dat'], SystemExit],
        [['bogus.dat'], SystemExit],
        [['-g', 'sample_input_1.json'], SystemExit],
        [['-f', 'sample_input_1.json', 'bogus.dat'], SystemExit],
        [['-f=sample_input_1.json', 'bogus.dat'], SystemExit],
        [['-f'], SystemExit],
        [['--file'], SystemExit],
        [['-f', 'no_file.dat'], FileNotFoundError],
    ])
    def test_cli_utils_02(self, mock_cli, expected_error):
        sys.argv[1:] = mock_cli
        with pytest.raises(expected_error):
            process_command_line()

    @pytest.mark.parametrize("mock_cli", [
        ['-f', 'sample_input_URLs_1.json'],
        ['-f=sample_input_URLs_1.json'],
        ['--file=sample_input_URLs_1.json'],
    ])
    def test_cli_utils_03(self, mock_cli):
        sys.argv[1:] = mock_cli
        file = process_command_line()
        assert os.path.isfile(file)
