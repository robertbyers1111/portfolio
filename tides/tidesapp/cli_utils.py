#!/bin/env python3
"""
MODULE: cli_utils - A module for processing the user's command line.
"""

import argparse
import os
import sys

def process_command_line():
    """
    Processes the command line. Returns the name of the input file.

    This is not a generic method. This method supports *ONLY* the
    tidesapp's CLI syntax.

    Uses argparse to process the user's command line.

    Currently only supports a filename argument (-f, or --file=)
    Returns the filename. If no filename argument was supplied, a
    value of None is returned.

    Args..
    (none)

    Returns..
    filename (str) the name of a file containing location URLs.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    args = parser.parse_args(sys.argv[1:])
    if not args.file:
        return None
    if not os.path.isfile(args.file):
        print(f"ERROR: {args.file} does not exist or is not a file")
        raise FileNotFoundError
    return args.file
