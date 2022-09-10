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

Rather than struggle for an indeterminate time trying to get my Python script using someone else's unofficial, and
oft-times no-longer maintained Python module, I decided the quickest solution for my need was to use Python to invoke
CLI sessions of the bluetoothctl utility ... as if I was running bluetoothctl from an interactive shell, but using Python.

This quickly proved to be very simple and very successful!

One unique aspect of this project is that it spawns external processes from Python. The approach I used to accomplish
this was to leverage the new-ish asyncio features of Python 3.x.

The code in this module makes extensive use of asyncio - albeit only in a very simple context (i.e., no queue of task
producers and consumers). My simple implementation is, however, very effective! The key requirement that necessitated
asyncio was the need to enable bluetooth scanning, leaving it in that mode while additional bluetoothctl commands are
issued. In other words, an asynchronous process is exactly what needs to be implemented!

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
    - bluetooth-adapters (installs - finds adapters but that's all)
    - bluetooth-connect (won't install due to dependency conflict with flask 2.2.2 and click 7.1.2/8.0)
    - pybluez (won't install)
    - btzen (won't install)

For information about the linux bluetooth stack, see https://ubuntu.com/core/docs/bluez
"""

import asyncio
import os
import psutil
import re
import sys
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from asyncio_utils import run_async


def assert_exists_and_executable(file):
    """
    Confirms whether a file exists and whether its permissions allow execution. Raises FileNotFoundError and
    PermissionError, respectively.
    """
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


class Pybluez_ez:

    BLUETOOTHCTL = "/usr/bin/bluetoothctl"
    INITD_BLUETOOTH = "/etc/init.d/bluetooth"

    def __init__(self):
        self.bluetoothctl = Pybluez_ez.BLUETOOTHCTL
        self.initd_bluetooth = Pybluez_ez.INITD_BLUETOOTH
        assert_exists_and_executable(self.bluetoothctl)
        assert_exists_and_executable(self.initd_bluetooth)
        self.bt_settings = {}
        self.bt_scanning_proc = None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Command primitives - Error checking and complex processing occurs only in higher
    #                      level methods.

    def devices(self):
        rc, stdout = run_btctl_cmd("devices")
        return rc, stdout

    def paired_devices(self):
        rc, stdout = run_btctl_cmd("paired-devices")
        return rc, stdout

    def info(self, device):
        rc, stdout = run_btctl_cmd(["info", device])
        return rc, stdout

    def trust(self, device):
        rc, stdout = run_btctl_cmd(["trust", device])
        return rc, stdout

    def untrust(self, device):
        rc, stdout = run_btctl_cmd(["untrust", device])
        return rc, stdout

    def pair(self, device):
        rc, stdout = run_btctl_cmd(["pair", device])
        return rc, stdout

    def cancel_pairing(self, device):
        rc, stdout = run_btctl_cmd(["cancel-pairing", device])
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

    def block(self, device):
        rc, stdout = run_btctl_cmd(["block", device])
        return rc, stdout

    def unblock(self, device):
        rc, stdout = run_btctl_cmd(["unblock", device])
        return rc, stdout

    def status(self):
        """
        Run '/etc/init.d/bluetooth status'

        Returns..
            (child_return_code (int), stdout (str)) - A tuple containing the child process' return code and the contents
                                                      of the child process' stdout and stderr.
        """

        rc, stdout = run_btsvc_cmd("status")
        return rc, stdout

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # High level methods - These methods rely on the command primitives to accomplish
    #                      more complex tasks.

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

    def check_if_scanning(self, check_if_enabled=True):
        """
        Checks whether the default bluetooth controller is currently set to scanning mode.

        Args..
            check_if_enabled - If set to True, then returns True if scanning is found to be active.
                               If set to False, then returns True if scanning is found to be inactive.

        Returns..
            True or False, depending on the input parameter check_if_enabled. See above.
        """

        if check_if_enabled:
            print("Checking if scanning is enabled..")
        else:
            print("Checking if scanning is disabled..")
        rc, stdout, bt_settings = btctl.show(verbose=False)
        if 'discovering' not in bt_settings.keys():
            print('ERROR: Unable to determine if bluetooth scanning is already enabled.', file=sys.stderr)
            raise ValueError
        if bt_settings['discovering'] == 'yes':
            if check_if_enabled:
                print('Confirmed that scanning is currently enabled. Returning True.')
                return True
            else:
                print('Scanning is not currently enabled. Returning False.')
                return False
        elif bt_settings['discovering'] == 'no':
            if check_if_enabled:
                print('Scanning is disabled. Returning False.')
                return False
            else:
                print('Confirmed that scanning is currently disabled. Returning True.')
                return True
        else:
            print(f"ERROR: invalid value for bluetooth discover mode: {bt_settings['discovering']}", file=sys.stderr)
            raise ValueError

    def check_if_scanning_enabled(self):
        return btctl.check_if_scanning(check_if_enabled=True)

    def check_if_scanning_disabled(self):
        return btctl.check_if_scanning(check_if_enabled=False)

    def scan_on(self):
        """
        Enable scanning on the host's bluetooth controller. An asynchronous process is spawned that keeps the scanning
        running until it is explicitly halted by some other means (usually the scan_off() method of this module)

        Returns..
            proc - An asyncio process object representing the process that enabled scanning. This process continues
                   running on the host after this method returns.

                   Also, stores the process as a class attribute. This simplifies terminating the process at a later time.

                   Returns None if scanning is already enabled.
        """

        print()
        print("Received request to enable bluetooth scanning")

        if btctl.check_if_scanning_enabled():
            print('NOTICE: bluetooth scanning is already enabled. Not attempting to re-enable.', file=sys.stderr)
            return None

        proc = asyncio.run(run_async(f'{Pybluez_ez.BLUETOOTHCTL} scan on'))

        print('Pause pi seconds then confirm scanning was in fact enabled..')
        sleep(3.14159)

        rc, stdout, bt_settings = btctl.show(verbose=False)

        if btctl.check_if_scanning_enabled():
            print('OK: bluetooth scanning is enabled.')
            self.bt_scanning_proc = proc
            return proc
        else:
            print('Unable to enable bluetooth scanning', file=stderr)
            return None

    def scan_off_via_asyncio(self):
        """
        If the current instance of this process had previously enabled scanning via an asyncio process, then the cleanest
        way to stop the scanning is by terminating that process. This method checks to see if an asyncio process for
        bluetooth scanning exists in memory and, if so, attempts to terminate it.

        TODO: There is a serious problem with killing the asyncio process..

        First of all, I'm using asyncio.create_subprocess_shell(), and the "bluetoothctl scan on" process is a child of
        the shell created by asyncio. I can kill the shell process, but the "bluetoothctl scan on" command remains running.

        The proper approach is to avoid spawning a shell by using asyncio.create_subprocess_exec(). But I am having
        difficulty getting this to work!

        Hence, for the time being, I am unable to reliably shut down a scanning process that was created in the same
        python runtime.

        I am, however, able to kill it if I run this python script a second time .. which will kill the process via
        python's psutil module.

        Until the issues are resolved, please avoid attempting to disable scanning in the same python session from which
        it was started.

        """

        # Constants for the return values..
        ACTIVE_OR_UNKNOWN = False
        INACTIVE = True

        if self.bt_scanning_proc is not None:
            print("Found asyncio process for bluetooth scanning. Will attempt to terminate it..")

            self.bt_scanning_proc.kill()

            if btctl.check_if_scanning_disabled():
                print('OK: bluetooth scanning is disabled.')
                self.bt_scanning_proc = None
                return INACTIVE
            else:
                print('WARNING: Unable to confirm bluetooth scanning was successfully disabled.', file=sys.stderr)
                return ACTIVE_OR_UNKNOWN

    def scan_off_via_cli(self):
        """
        Attempt to disable bluetooth scanning via the CLI command "bluetoothctl scan off"

        This does not always succeed, particularly when there is an explicit 'bluetoothctl scan on' process
        running on the system. In this case, a method that kills the scanning process should be used instead.

        Returns..
            True - If scanning is confirmed to be inactive
            False - If scanning is active and we weren't able to disable it.
        """

        # Constants for the return values..
        ACTIVE_OR_UNKNOWN = False
        INACTIVE = True

        print()
        print("Received request to disable bluetooth scanning via the bluetoothctl CLI")

        if btctl.check_if_scanning_disabled():
            print('NOTICE: bluetooth scanning is already disabled. Not attempting to disable.', file=sys.stderr)
            return INACTIVE

        print('Detected that scanning is currently enabled. Continue attempting to disable..')

        rc, stdout = run_btctl_cmd(["scan", "off"])

        print('Pausing pi seconds then confirming scanning was in fact disabled..')
        sleep(3.14159)

        rc, stdout, bt_settings = btctl.show(verbose=False)

        if btctl.check_if_scanning_disabled():
            print('OK: bluetooth scanning is disabled.')
            return INACTIVE
        else:
            print('WARNING: Unable to confirm bluetooth scanning was successfully disabled.', file=sys.stderr)
            return ACTIVE_OR_UNKNOWN

    def scan_off_via_process_kill(self):
        """
        Brute force kill of the scanning process. This is needed because the "bluetoothctl scan off" command fails
        if an explicit "bluetoothctl scan on" command is already running on the host.
        """

        killed = 0
        for proc in psutil.process_iter(['name', 'cmdline', 'pid', 'username']):
            if 'scan' in proc.cmdline():
                if 'bluetoothctl' in proc.info['name'] and len(proc.info['cmdline']) == 3:
                    if 'bluetoothctl' in proc.info['cmdline'][0] \
                            and proc.info['cmdline'][1] == 'scan' \
                            and proc.info['cmdline'][2] == 'on':
                        print(f'Killing bluetooth scan proc: {proc}')
                        proc.kill()
                        killed += 1

        if killed > 0:
            for proc in psutil.process_iter(['name', 'cmdline', 'pid', 'username']):
                if 'scan' in proc.cmdline():
                    if 'bluetoothctl' in proc.info['name'] and len(proc.info['cmdline']) == 3:
                        if 'bluetoothctl' in proc.info['cmdline'][0] \
                                and proc.info['cmdline'][1] == 'scan' \
                                and proc.info['cmdline'][2] == 'on':
                            print(f'ERROR: bluetooth scanning proc still active: {proc}', file=stderr)
                            return False

        return True

    def scan_off(self):
        """
        Disable bluetooth scanning on the host's default controller. First we check if an asyncio process exists for the
        bluetooth scanning and, if so, we terminate it. If that fails, we try via the bluetoothctrl CLI. If that fails,
        our last attempt is to discover and kill any existing scanning processes.
        """

        scan_status = self.scan_off_via_asyncio()
        if not scan_status:
            scan_status = self.scan_off_via_cli()
        if not scan_status:
            scan_status = self.scan_off_via_process_kill()
        return scan_status


if __name__ == '__main__':
    btctl = Pybluez_ez()
    btctl.scan_off()
    btctl.status()
    btctl.show()
    btctl.devices()
    btctl.scan_on()
    print('Sleeping 8 seconds..')
    sleep(8)
