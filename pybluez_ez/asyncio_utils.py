#!/bin/env python3
"""
A module containing a few helper methods for using python's asyncio capabilities
"""

import asyncio
import os
import psutil
import re
import sys
from time import sleep
from subprocess import Popen, PIPE, STDOUT


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

