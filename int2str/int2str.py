#!/bin/env python3
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
int2str - A library for generating string representations of integers.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OVERVIEW:

    The main method provided by this module is 'int2str'. It accepts an
    integer and, optionally, a language choice, and returns a string
    containing the words representation of that integer.

    Acceptable range of integers is set by the Int2str class variables
    MIN and MAX. See code for current supported range.

    Currently only English is supported. There is an enum class
    (Int2strLang) which will be used to select a language to override
    the default (English).

    Invalid input results in a ValueError exception.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EXAMPLE USAGE:

    from int2str import int2str
    int2str(0)
    int2str(1)
    int2str(55)
    int2str(-1000000)
    int2str(1000000)

    >>> zero
    >>> one
    >>> fifty five
    >>> negative one million
    >>> one million

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MOTIVATION:

    Given some integer (N) as an argument, return a string representation
    of that integer.

    For example, using the capability in the python REPL (implemented as a
    function called _int2str_) may look like this:

    >>> int2str(5)
    'five'
    >>> int2str(55)
    'fifty-five'

Copyright 2022 Robert Byers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from enum import Enum, auto

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Int2strLang(Enum):
    """
    An Enum class used to select the target language.
    """
    ENGLISH = auto()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Int2str():
    """
    The main class for the int2str library
    """

    # Constraints on the integers to be translated
    MIN = -999999999
    MAX = 999999999

    # A dictionary storing all the building-block words for integers
    LEXICON = {}

    # Integer words in English
    LEXICON[Int2strLang.ENGLISH] = {
        -1: 'negative',
        0: 'zero',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
        6: 'six',
        7: 'seven',
        8: 'eight',
        9: 'nine',
        10: 'ten',
        11: 'eleven',
        12: 'twelve',
        13: 'thirteen',
        14: 'fourteen',
        15: 'fifteen',
        16: 'sixteen',
        17: 'seventeen',
        18: 'eighteen',
        19: 'nineteen',
        20: 'twenty',
        30: 'thirty',
        40: 'forty',
        50: 'fifty',
        60: 'sixty',
        70: 'seventy',
        80: 'eighty',
        90: 'ninety',
        100: 'hundred',
        1000: 'thousand',
        1000000: 'million',
        1000000000: 'billion',
    }


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __int2str_util__(self, n, lang):
        """
        Receives an integer from 1 to 999. Returns the words equivalent.

        ==> THIS METHOD IS FOR INTERNAL USE ONLY.

        This method translates any integer between 1 and 999. It is used
        to translate the number of single units, as well as the number of
        thousands, millions, etc. As such, it is used as a building-block
        to build the larger numbers passed into int2str()

        This method is only to be called internally. We assume bounds and
        type checking of the paramaters has already taken place (in the
        scope of the calling method). Therefore, only a minimal bounds
        check is performed here.

        Args..

            n, An integer in the range 1 <= n <= 999

            lang, An Int2strLang enum specifying the language to be used.
                  Default: ENGLISH

        Returns..

            the_number, A string representation of the integer, in
                        the given language

        """

        # Fail if n is out of range
        if n < 1 or n > 999:
            raise ValueError

        # Initialize the return value
        the_number = ''

        # Process hundredths
        if n >= 100:
            num_hundreds = int(n/100)
            num_hundreds_word = Int2str.LEXICON[lang][num_hundreds]
            the_number += ' ' + num_hundreds_word + ' ' + Int2str.LEXICON[lang][100]
            # Remove the hundredths, so we can process the rest of the number
            n %= 100

        # Process 20, 30, ... 90
        if n >= 20 and n <= 99:
            num_tenths = int(n/10)*10
            num_tenths_word = Int2str.LEXICON[lang][num_tenths]
            the_number += ' ' + num_tenths_word
            # Remove the tenths, so we can process the rest of the number
            n %= 10

        # Process 1 through 19
        if n >= 1 and n <= 19:
            the_number += ' ' + Int2str.LEXICON[lang][n]

        # That is all
        return the_number.strip()


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def int2str(self, n, lang=None):
        """
        Accepts an integer and language (optional). Returns the word equivalent.

        This method accepts an integer and language. Returns a string containing
        the spoken-word equivalent of an integer in the selected language.

        Args..

            n, An integer in the range 1 <= n <= 999

            lang, An Int2strLang enum specifying the language to be used.
                  Default: ENGLISH

        Returns..

            the_number, A string representation of the integer, in
                        the given language
        """

        # Use default language if none was passed in
        if not lang:
            lang = Int2strLang.ENGLISH

        # Fail if n is not an integer
        if not isinstance(n, int):
            raise ValueError

        # Fail if n is out of range
        if n < Int2str.MIN or n > Int2str.MAX:
            raise ValueError

        # Special case: zero
        if n == 0:
            return 'zero'

        # Initialize the return string as 'negative' for negative n, or an empty string for non-negative n
        if n < 0:
            the_number = Int2str.LEXICON[lang][-1]
        else:
            the_number = ''

        # Ditch the negative sign, we've already processed it
        n = abs(n)

        # Process millions
        if n >= 1000000:
            num_millions = int(n/1000000)
            num_millions_string = self.__int2str_util__(num_millions, lang)
            the_number += ' ' + num_millions_string + ' ' + Int2str.LEXICON[lang][1000000]
            # Remove the millions, so we can process the rest of the number
            n %= 1000000

        # Process thousandths
        if n >= 1000:
            num_thousandths = int(n/1000)
            num_thousandths_string = self.__int2str_util__(num_thousandths, lang)
            the_number += ' ' + num_thousandths_string + ' ' + Int2str.LEXICON[lang][1000]
            # Remove the thousandths, so we can process the rest of the number
            n %= 1000

        # Process ones, tens and hundreds
        if n > 0:
            the_number += ' ' + self.__int2str_util__(n, lang)

        # That is all
        return the_number.strip()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def int2str(n, lang=None):
    """
    Accepts an integer and language (optional). Returns the word equivalent.

    This is a wrapper method for int2str(). Inside this wrapper we
    instantiate an Int2str() object and then invoke the class method
    int2str(), returning its result.

    Args..

        n, An integer in the range 1 <= n <= 999

        lang, An Int2strLang enum specifying the language to be used.
              Default: ENGLISH

    Returns..

        the_number, A string representation of the integer, in
                    the given language
    """

    obj = Int2str()
    return obj.int2str(n, lang)

