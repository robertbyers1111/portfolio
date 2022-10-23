#!/bin/env
"""
A module containing a few tidesapp-specific json utilities.
"""

def check_dict_keys(dictionary, num_keys, expected_keys, data=None):
    """
    Perform a sanity check on a dictionary.
    
    Args...
    
        dictionary (dict) The dictionary to be checked
    
        num_keys (int) The number of keys expected to be found in the dictionary
    
        expected_keys (list of strings) The values of the expected keys
    
        data (str) (optional) If supplied, it is a string that further clarifies where the dictionary from. Used in
                              error messages only.

    Returns...

        None

    Actions...

        This method will raise a ValueError if a problem is detected.
        Otherwise it returns None.
    """

    if data is None:
        data = 'N/A'
    if type(dictionary) != dict:
        print(f"\nERROR: {data} is not a python dictionary")
        raise ValueError
    if len(dictionary.keys()) != num_keys:
        print(f"\nERROR: expected {num_keys} in {data}, but found {len(dictionary.keys())}")
        raise ValueError
    for key in expected_keys:
        if key not in dictionary.keys():
            print(f"\nERROR: unexpected key {key} in {data}")
            raise ValueError

