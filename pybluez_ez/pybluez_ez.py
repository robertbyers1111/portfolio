#!/bin/env python3
"""
A module to perform a very limited set of bluetooth operations on a linux system with the linux bluetooth stack ("bluez")

STATUS:

    This module is WORK-IN-PROGRESS!!!! I've uploaded it to github prior to being fully operational only because it
    demonstrates my use of the Python asyncio module. I am continuing to develop this module (Sep 2022) and expect to
    have a working version checked in by the end of Sep 2022.

MOTIVATION:

I developed this module to provide a personal workaround for the dreaded "Software caused connection abort" error that
frequently occurs on linux distributions with the bluez bluetooth stack. The symptom is that a bluetooth device will
establish a connection with the bluetooth subsystem on a linux host - but within a few seconds it will disconnect. The
event is seen in /var/log/syslog as a message similar to..

bluetoothd[841]: profiles/audio/avdtp.c:avdtp_connect_cb() connect to 58:FC:C6:40:41:19: Software caused connection abort (103)

Many users have reported this problem on various forums. Some of them have found a successful workaround in the use of
/usr/bin/bluetoothctl as a command-line approach to manually adding a device to the host's bluetooth subsystem. I have
had success with this approach on my own system.

The workaround is exceedingly simple ... use the bluetoothctl CLI tool to add a device rather than relying on the
bluez helper apps. For example, I've had success using this procedure..

1. (turn on my bluetooth headset - possibly placing it into pairing mode)
2. bluetoothctl scan on
3. bluetoothctl trust MAC
4. bluetoothctl pair MAC
5. bluetoothctl connect MAC

.. if my headset is already a known device I may have to remove it first (bluetoothctl remove MAC), and I may have to
put my headset into pairing mode. The procedure has been 100% reliable for me.

I first decided to write a bash script to automate the procedure, but due to the need to properly manage the bluetooth
scanning mode (step 2), my bash script very quickly became ugly. It became clear that a Python solution would be much
clearer and cleaner.

But then I had spotty results attempting to use any of the many Python modules from pypi.org that support bluetooth on
linux.

Rather than struggle for an indeterminate time trying to get my Python script using someone else's unofficial, and oft-
times no-longer maintained Python module, I decided the quickest solution for my need was to use Python to invoke CLI
sessions of the bluetoothctl utility ... as if I was running bluetoothctl from an interactive shell, but using Python.

This quickly proved to be very simple and very successful!

One unique aspect of this project is that it spawns external processes from Python. The approach I used to accomplish
this was to leverage the new-ish asyncio features of Python 3.x.

The code in this module makes extensive use of asyncio - albeit only in a very simple context (ie., no queue of task
producers and consumers). My simple implementation is, however, very effective! The key requirement that necessitated
asyncio was the need to enable bluetooth scanning. This feature needs to be enabled, and then left enabled while other
tasks are performed. In other words, an asynchronous process is exactly what needs to be implemented!

The process that enables bluetooth scanning needs to be left alone while I perform the remaining tasks to get my headset
connected. Asyncio is exactly the correct tool for doing this. With it, I am able to enable bluetooth scanning, let it
run in background, continue with the other steps, and then, once I am finished connecting my headset, I can terminate
the scanning process.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: I have had very spotty success with various bluetooth modules from pypi.org. Therefore, this module takes a
different approach by avoiding python modules and instead launches external instances of the bluetoothctl command
line tool (/usr/bin/bluetoothctl)

The modules from pypi.org that aren't working for me include..

    - pybluez2 (installs - but never finds any bt devices)
    - bumble (installs - but supplied apps don't run)
    - bluetooth-adapters (installs - finds adapters but the results are packed - not sure how to unpack)
    - bluetooth-connect (won't install due to dependency conflict with flask 2.2.2 and click 7.1.2/8.0)
    - pybluez (won't install)
    - btzen (won't install)

See https://ubuntu.com/core/docs/bluez
"""

import asyncio
import os
import re
import sys
from time import sleep
from subprocess import Popen, PIPE, STDOUT


def assert_exists_and_executable(file):
    if not os.path.isfile(file):
        print(f"\nERROR: {file} does not exist or is not a file", file=sys.stderr)
        raise FileNotFoundError
    if not os.access(file, os.X_OK):
        print(f"\nERROR: {file} is not executable", file=sys.stderr)
        raise PermissionError


def run_btsvc_cmd(subcmd, verbose=None, fail_to_exception=None):
    """
    Run a specific bluetooth service command (/etc/init.d/bluetooth)

    Args..
        subcmd (list of str) - the /etc/init.d/bluetooth sub-command to be run, followed by the sub-command's parameters.

        verbose (bool) - If true, the command's return code, stdout and stderr will be printed. Default: True

        fail_to_exception (bool) - If true, a ChildProcessError is raised if the return code is non-zero. Default: False

    Returns..
        child_return_code (int), stdout (str) - A tuple containing the child process' return code and the contents
                                                of the child process' stdout and stderr.
    """

    if verbose is None:
        verbose = True

    if fail_to_exception is None:
        fail_to_exception = False

    if isinstance(subcmd, str):
        full_cmd = [Pybluez_ez.INITD_BLUETOOTH, subcmd]
    elif isinstance(subcmd, list):
        full_cmd = [Pybluez_ez.INITD_BLUETOOTH] + subcmd
    else:
        print(f"ERROR: {subcmd} is neither str nor list")
        raise TypeError

    forked = Popen(full_cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = forked.communicate()[0]
    rc = forked.returncode

    if verbose:
        print()
        print(f"CMD: {full_cmd}")
        print(f"rc: {rc}")
        print(f"{stdout.decode()}")

    if fail_to_exception:
        if rc != 0:
            raise ChildProcessError

    return rc, stdout


def run_btctl_cmd(subcmd, verbose=None, fail_to_exception=None):
    """
    Run a specific bluetoothctl command

    Args..
        subcmd (list of str) - the bluetoothctl sub-command to be run, followed by the sub-command's parameters.

        verbose (bool) - If true, the command's return code, stdout and stderr will be printed. Default: True

        fail_to_exception (bool) - If true, a ChildProcessError is raised if the return code is non-zero. Default: False

    Returns..
        child_return_code (int), stdout (str) - A tuple containing the child process' return code and the contents
                                                of the child process' stdout and stderr.
    """

    if verbose is None:
        verbose = True

    if fail_to_exception is None:
        fail_to_exception = False

    if isinstance(subcmd, str):
        full_cmd = [Pybluez_ez.BLUETOOTHCTL, subcmd]
    elif isinstance(subcmd, list):
        full_cmd = [Pybluez_ez.BLUETOOTHCTL] + subcmd
    else:
        print(f"ERROR: {subcmd} is neither str nor list")
        raise TypeError

    forked = Popen(full_cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = forked.communicate()[0]
    rc = forked.returncode

    if verbose:
        print()
        print(f"CMD: {full_cmd}")
        print(f"rc: {rc}")
        print(f"{stdout.decode()}")

    if fail_to_exception:
        if rc != 0:
            raise ChildProcessError

    return rc, stdout


async def run_wait(cmd):
    """
    Run an async command, blocking until it completes. Upon completion, print the command's stdout and stderr.

    Args..
        cmd (str) - the full command to be run, including executable and all command line arguments
    """

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def run_async(cmd):
    """
    Run an external command asynchronously, without blocking. Returns the async process object.

    Args..
        cmd (str) - the full command to be run, including executable and all command line arguments

    Returns..
        proc () - The process' asyncio object (<class 'asyncio.subprocess.Process'>)
    """

    return await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)


class Pybluez_ez:

    BLUETOOTHCTL = "/usr/bin/bluetoothctl"
    INITD_BLUETOOTH = "/etc/init.d/bluetooth"

    def __init__(self):
        self.bluetoothctl = Pybluez_ez.BLUETOOTHCTL
        self.initd_bluetooth = Pybluez_ez.INITD_BLUETOOTH
        assert_exists_and_executable(self.bluetoothctl)
        assert_exists_and_executable(self.initd_bluetooth)
        self.bt_settings = {}

    def status(self):
        """
        Run '/etc/init.d/bluetooth status'

        Returns..
            (child_return_code (int), stdout (str)) - A tuple containing the child process' return code and the contents
                                                      of the child process' stdout and stderr.
        """

        rc, stdout = run_btsvc_cmd("status")
        return rc, stdout

    def show(self, verbose=None):
        """
        Run 'bluetoothctl show'. Save settings to a dictionary.

        Args..
            verbose (bool) - If true, the command's return code, stdout and stderr will be printed. Default: True

        Returns..

            A tuple containing the following elements..
                (
                  child_return_code (int) - child process' return code.
                  stdout (str) - stdout (and stderr) of the command after it has completed.
                  bt_settings (dict) - A dictionary containing the settings parsed from the command output.
                )
        """

        if verbose is None:
            verbose = True

        rc, stdout = run_btctl_cmd("show", verbose)

        self.bt_settings = {}

        pattern1 = re.compile("^\s*(?P<key>UUID:\s+[^(]+)\((?P<value>.*)\)\s*$")
        pattern2 = re.compile("^\s*(?P<key>[^:]+):\s+(?P<value>.*)$")
        pattern3 = re.compile("^\s*(?P<key>Controller)\s+(?P<value>\S+)")

        for line in stdout.decode().split('\n'):
            line = line.lower()
            for pattern in [pattern1, pattern2, pattern3]:
                parsed = re.match(pattern, line)
                if parsed is not None:
                    key = parsed.group('key').strip()
                    value = parsed.group('value').strip()
                    self.bt_settings[key] = value
                    break

        return rc, stdout, self.bt_settings

    def devices(self):
        rc, stdout = run_btctl_cmd("devices")
        return rc, stdout

    def paired_devices(self):
        rc, stdout = run_btctl_cmd("paired-devices")
        return rc, stdout

    def info(self, device):
        rc, stdout = run_btctl_cmd(["info", device])
        return rc, stdout

# TODO: Add unit tests for these..

    def trust(self, device):
        rc, stdout = run_btctl_cmd(["trust", device])
        return rc, stdout

    def pair(self, device):
        rc, stdout = run_btctl_cmd(["pair", device])
        return rc, stdout

    def connect(self, device):
        rc, stdout = run_btctl_cmd(["connect", device])
        return rc, stdout

    def disconnect(self, device):
        rc, stdout = run_btctl_cmd(["disconnect", device])
        return rc, stdout

    def remove(self, device):
        rc, stdout = run_btctl_cmd(["remove", device])
        return rc, stdout

    def scan_on(self):

        print()
        print("Received request to enable bluetooth scanning")

        print("Check if scanning is already enabled..")
        rc, stdout, bt_settings = btctl.show(verbose=False)
        if 'discovering' not in bt_settings.keys():
            print('ERROR: Unable to determine if bluetooth scanning is already enabled.', file=sys.stderr)
            return None
        elif bt_settings['discovering'] == 'yes':
            print('NOTICE: bluetooth scanning is already enabled. Not attempting to re-enable.', file=sys.stderr)
            return None
        else:
            print('Detected that scanning is not currently enabled. Continue attempting to enable..')

            proc = asyncio.run(run_async(f'{Pybluez_ez.BLUETOOTHCTL} scan on'))

            print('Pausing pi seconds then confirm scanning was in fact enabled..')

            sleep(3.14159)
            rc, stdout, bt_settings = btctl.show(verbose=False)

            if 'discovering' not in bt_settings.keys():
                print('ERROR: Unable to determine if bluetooth scanning is already enabled.', file=sys.stderr)
                return None
            elif bt_settings['discovering'] != 'yes':
                print('ERROR: Unable to confirm bluetooth scanning was successfully enabled.', file=sys.stderr)
                return None
            else:
                print('Oh Joy! Oh rapture! BT scanning is enabled!')

            return proc

    def scan_off(self):
        rc, stdout = run_btctl_cmd(["scan off"])
        return rc, stdout


if __name__ == '__main__':
    btctl = Pybluez_ez()
    btctl.status()
    btctl.show()
    btctl.devices()
    btctl.scan_on()
    pass
