#!/bin/env pytest
"""
Unit tests for pybluez_ez
"""

import pytest
from pybluez_ez import my_run
from pybluez_ez import Pybluez_ez


class Tests_pybluez_ez:

    def test_00_initd_bluetooth_status(self):
        bluetoothctl = Pybluez_ez()
        rc, stdout = bluetoothctl.status()
        assert rc == 0
        print('\n', stdout.decode())
        pass

    def test_01_bluetoothctl_show(self):
        bluetoothctl = Pybluez_ez()
        rc, stdout = bluetoothctl.show()
        assert rc == 0
        print('\n', stdout.decode())

    def test_02_bluetoothctl_devices(self):
        bluetoothctl = Pybluez_ez()
        rc, stdout = bluetoothctl.devices()
        assert rc == 0
        print('\n', stdout.decode())

    def test_03_bluetoothctl_paired_devices(self):
        bluetoothctl = Pybluez_ez()
        rc, stdout = bluetoothctl.paired_devices()
        assert rc == 0
        print('\n', stdout.decode())

    @pytest.mark.parametrize("device", ["58:FC:C6:40:41:19"])
    def test_04_bluetoothctl_info(self, device):
        bluetoothctl = Pybluez_ez()
        rc, stdout = bluetoothctl.info(device)
        assert rc == 0
        print('\n', stdout.decode())

    def test_99_asyncio_my_run(self):
        my_run('/bin/ls -l /etc/hosts')
        pass
