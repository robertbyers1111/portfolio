#!/bin/env python3
"""
A module for manipulating dates and times for the tidesapp app.
"""

from datetime import datetime, date


def day2datetime(queried_day: int):
    """
    Accepts a day-of-month. Returns datetime object equivalent.

    The motivation for this method is that the tideschart.com weekly
    tides tables display only a day-of-month integer. This DOM-
    rendered table displays these day-of-month values relative to the
    current day. Therefore, it is possible to determine the actual
    date referenced by each of these day-of-month numbers.

    For example, if the user visits the table on 7/4/2022 and is
    presented with tides data for the 4th, 5th, 6th, 7th, 8th,
    9th and 10th of the month, we know these are all relative to
    7/4/2022.

    This method uses this knowlege to convert a day-of-month integer
    from the weekly tides table to a Python datetime value.

    Appropriate handling of month overflow and year overflow
    conditions are fully supported.

    Args..
        queried_day: (int) The day of month to be queried

    Returns..
        A Python datetime object corresponding to the queried day
    """

    # If the inputted day is in a string, convert it to int
    if isinstance(queried_day, str):
        queried_day = int(queried_day)

    # Make sure the value passed in is an integer
    if not isinstance(queried_day, int):
        raise ValueError

    # Get today's datetime
    today_datetime = date.today()

    # Initialize the queried day's month and year
    queried_month = today_datetime.month
    queried_year = today_datetime.year

    # Adjust month and year if we rolled into a new month or year
    if queried_day < today_datetime.day:
        queried_month += 1
    if queried_month > 12:
        queried_month = 1
        queried_year += 1

    # Return the desired datetime
    return datetime(queried_year, queried_month, queried_day)


def timestr2time(timestr):
    """
    Input "HH:MM AM" or "HH:MM PM". Returns a python datetime object.

    The returned object is a full python datetime object, but only its
    hour, minute and second are set here. The caller must be aware of
    this!

    Args..
    timestr (str) A string with the time of day to be converted.

    Returns..
    timeval (datetime) A python datetime object with its hour,
            minute set from the input string
    """
    # Remove any spaces from the input
    timestr = ''.join(timestr.split())
    # Return the datetime object
    return datetime.strptime(timestr, "%I:%M%p")


def date_time_combine(dateval, timeval):
    """
    Input a date and time of day. Combine them and return a datetime.

    Args..
    dateval (datetime) A python datetime object. Only the year,
                       month and day will be used.
    timeval (datetime) A python datetime object. Only the hour,
                       minute and second will be used.

    Returns..
    datetimeval (datetime) A python datetime object with its year,
                           month, day taken from dateval and its hour,
                           minute, second taken from timeval.
    """
    return datetime(
        dateval.year, dateval.month, dateval.day,
        timeval.hour, timeval.minute, 0
    )
