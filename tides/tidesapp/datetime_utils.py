#!/bin/env python3
"""
MODULE: datetime_utils - A module for manipulating dates and times for the tidesapp app.
"""

from datetime import datetime, date

def day2datetime(queried_day):
    """
    Returns a python datetime object representing the inputted day, auto filling year and month.

    The year and month are assumed to be the current year and month, unless day < today, in
    which case the month is assumed to be the subsequent month.

    Motivation: This method exists because the tideschart.com weekly tide table provides *only*
    the day-of-month number for the tides covering the next seven days. Since the first row
    of tide data is *always* for the current day, we can easily deduce the year and month.

    Args
    queried_day: (int) The day of month to be queried

    :Returns: (datetime) python datetime object corresponding to the queried day
    """

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

