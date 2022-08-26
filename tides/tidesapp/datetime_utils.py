#!/bin/env python3
"""
MODULE: datetime_utils - A module for manipulating dates and times for the tidesapp app.
"""

from datetime import datetime, date

def day2datetime(queried_day):
    """
    Accepts a day-of-month integer. Returns a datetime object equivalent.

    This is not a generic method. This method supports *ONLY* the
    requirements of the tidesapp application.

    The motivation for this method is that the tideschart.com weekly
    tides tables display only a day-of-month integer. This DOM-rendered
    table displays these day-of-month values relative to the current 
    day. Therefore it is possible to determine the actual date referenced
    by each of these day-of-month numbers.

    For example, if the user visits the table on 7/4/2022 and is presented
    with tides data for the 4th, 5th, 6th, 7th, 8th, 9th and 10th of the
    month, we know these are all relative to 7/4/2022.

    This method uses this knowlege to convert a day-of-month integer from
    the weekly tides table to a Python datetime value.

    Appropriate handling of month overflow and year overflow conditions
    are fully supported.

    Args..
        queried_day: (int) The day of month to be queried

    Returns..
        A Python datetime object corresponding to the queried day
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

