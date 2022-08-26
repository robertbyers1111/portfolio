#!/bin/env python3
"""
Retrieve tide data for multiple sites. Process and display results.

This application uses Selenium to visit a site containing tide charts.
Tide data from one or more locations are gathered, processed and
displayed. Tide data is retrived from www.tideschart.com.

Command line usage..

    tidesapp.py -f file

where file is a JSON file containing a list of URLs. There is no
specific limit on the number of URLs, tidesapp will query tide
data from each.

This script should run from most any system with python, selenium
and the Chrome webdriver. There are some OS-specific (linux)
operations that require running the app's test suite in a linux
environment (*todo: remove this limitation!*).

I selected tideschart.com for retrieving tide data. It supports
retrieval of weekly tide data for most US beaches via a simple URL
formulation. For example, to retrieve the current week's tide data
for Newburyport, MA, navigating a browser to the following URL
is sufficient..

    https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/

The input file is JSON formatted and contains a list of URLs.
For example..

{
    "URLs": [
        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Salisbury/"},
        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/"},
        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Rowley/"},
        ]
}
"""

import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from datetime_utils import (day2datetime, timestr2time,
                            date_time_combine)
from cli_utils import process_command_line

class TidesApp():

    """ Constants """

    # URLs for querying tide data for specific location names. If charting geo-trends, best to keep this list
    # in geographic north-to-south order.
    DEFAULT_URLS = [
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Salisbury/"},
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/"},
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Rowley/"},
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Crane-Beach/"},
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Wingaersheek-Beach/"},
        {'URL': "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Rockport/"},
    ]

    # XPATHs
    weekly_table_xpath = r'//table/child::caption[contains(text(),"Tide table for") and contains(text(), "this week")]/../tbody/tr'


    def load_user_locations(self, file=None):
        """
        Load the list of locations from disk into the tidesapp object.

        Basic sanity checks are performed, after which the list is
        saved and the method returns.

        Args:
        file - (str) A JSON-formatted file containing a list of URLs.
               Each URL should be a valid tideschart.com request.
               If no filename is passed in, a default list is loaded.

        Returns: (nothing)
        """

        if not file:
            self.locations = TidesApp.DEFAULT_URLS
        else:
            with open(file) as fh:
                data = json.load(fh)
                if not 'URLs' in data.keys():
                    print(f"ERROR: No URLs retrieved from {file}")
                    raise ValueError
                else:
                    self.locations = data['URLs']

        for location in self.locations:
            if not isinstance(location['URL'], str):
                raise ValueError
            if not location['URL'].startswith(
                    r"https://www.tideschart.com/"):
                raise ValueError


    def parse_high_tide_data(self, data):
        """
        Parse a single row data. Return a list of high tides.

        Args..
        data (str): A string extracted from the DOM for one row.
             Contains tide data for one day.

        Returns..
        tides[]: a list of high tide times (times are expressed
                 as python datetime
        """

        # Sample data to be parsed:
        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm'
        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm'
        # Notes..
        # (1) The web page indicates high tide with unicode character
        # up triangle, and low tide with down triangle.
        # (2) It is possible to have only three tides in a day!

        # This regex will parse any data adhering to the format
        # in the above examples..

        pattern = re.compile("^\s*" + \
        "(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+" + \
        "(?P<dayno>\d+)\s+" + \
        "(?P<tide1_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide1_hilo>(?:▲|▼))\s+(?P<tide1_height>\d+.\d+)\s*ft\s+" + \
        "(?P<tide2_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide2_hilo>(?:▲|▼))\s+(?P<tide2_height>\d+.\d+)\s*ft\s+" + \
        "(?P<tide3_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide3_hilo>(?:▲|▼))\s+(?P<tide3_height>\d+.\d+)\s*ft\s+" + \
        "(?:(?P<tide4_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide4_hilo>(?:▲|▼))\s+(?P<tide4_height>\d+.\d+)\s*ft\s+|)" + \
        "▲\s*(?P<sunrise>\d+:\d\d\s*(?:am|pm))\s+" + \
        "▼\s*(?P<sunset>\d+:\d\d\s*(?:am|pm))\s*$")

        # Get rid of all newlines in the data stream, they may be
        # safely ignored in this method
        data = re.sub('\n', ' ', data)

        # Parse the row's data..
        matched = re.match(pattern, data)
        if not matched:
            print(f"ERROR: Tide data not parsed: {data}")
            raise ValueError

        # Convert the day to a datetime
        this_day = day2datetime(matched.group('dayno'))

        # Assemble the list of tides
        this_day_tides = []
        for timestr, hilo in [
            (matched.group('tide1_time'), matched.group('tide1_hilo')),
            (matched.group('tide2_time'), matched.group('tide2_hilo')),
            (matched.group('tide3_time'), matched.group('tide3_hilo')),
            (matched.group('tide4_time'), matched.group('tide4_hilo'))
        ]:
            # Check if this tide data is for a high tide or low tide
            if hilo == '▲':
                # ok, it is for a high tide! Continue processing..

                # Convert time (e.g., "3:32 am") to a datetime object
                this_tide_time = timestr2time(timestr)
                # Combine with the day's datetime
                this_tide_datetime = date_time_combine(this_day,
                                                       this_tide_time)
                # Append the datetime
                this_day_tides.append(this_tide_datetime)

        if len(this_day_tides) < 1:
            print(f"ERROR: No high tide data found for: {data}")
            raise ValueError
        if len(this_day_tides) > 2:
            print(f"ERROR: Too many high tides found for: {data}")
            raise ValueError

        # TODO..
        # Return the list of tides for this location

        return []
    
    def get_weekly_tides(self, URL):
        """
        Retrive tide data for one location. Return a list of tides
        for the upcoming week.

        This method navigates the browser to a URL which renders
        weekly tide data for a particular location. The table of tide
        data is located in the DOM and, for each day in the table,
        the tide data are extracted and saved to the weekly_tides
        object.

        The browser object (self.driver) is assumed to exist.

        Args..

        URL (str): A URL, starting with 'https://www.tideschart.com/'
            that renders a weekly tide table for one location.

        Returns..
        weekly_tides, a list of high tides over one week for a
        particular location
        """

        self.driver.get(URL)
        self.wait.until(EC.presence_of_element_located((By.XPATH, TidesApp.weekly_table_xpath)))
        weekly_tides_DOM = self.driver.find_elements_by_xpath(TidesApp.weekly_table_xpath)
        if not len(weekly_tides_DOM) == 7:
            raise ValueError
        weekly_tides_one_location = []
        for i in range(7):
            weekly_tides_one_location.append(self.parse_high_tide_data(weekly_tides_DOM[i].text))
        return weekly_tides_one_location

    def mainapp(self):
        """
        This method is the main entry point for the app. Major tasks
        include..

        Parsing the user's command line
        Loading the user's location URLs into the app
        Initializing the webdriver
        Calling the weekly tides retriver for each of the locations
        """

        file = process_command_line()
        self.load_user_locations(file)
        self.driver = driver = webdriver.Chrome()
        self.wait = wait = WebDriverWait(driver, 30)
        weekly_tides = {}
        for URL in self.locations:
            weekly_tides[URL] = self.get_weekly_tides(URL)
        driver.close()

if __name__ == '__main__':
    TidesApp().mainapp()
