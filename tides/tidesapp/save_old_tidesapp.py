commit e6ca2152a864eddb32087a0f743dbbeaaebbcc79
Author: robertbyers1111 <robertbyers1111@gmail.com>
Date:   Mon Aug 29 19:51:21 2022 -0400

    Rename tidesapp_viaSelenium.py -> tidesapp.py

diff --git a/tides/tidesapp/tidesapp.py b/tides/tidesapp/tidesapp.py
new file mode 100755
index 0000000..d90f18e
--- /dev/null
+++ b/tides/tidesapp/tidesapp.py
@@ -0,0 +1,454 @@
+#!/bin/env python3
+"""
+Retrieve tide data for multiple sites. Process and display results.
+
+This application uses Selenium to visit a site containing tide charts. Tide data from one or more
+locations are gathered and processed.
+
+I selected tideschart.com for retrieving tide data. It supports retrieval of weekly tide data for
+most US beaches via a simple URL formulation. For example, to retrieve the current week's tide data
+for Newburyport, MA, navigating a browser to the following URL is sufficient..
+
+    https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/
+
+In addition, tideschart.com has a search feature, which is also used by this app.
+
+This app operates in one of two modes..
+
+[Operational Mode 1]
+
+    If the input file contains URLs, the URLs are used to navigate directly to a location's tide data.
+
+[Operational Mode 2]
+
+    If the input file contains place names and hints, the place names are entered in the search box
+    at tideschart.com, and the hints are used to find the desired place from the search results.
+
+Command line usage..
+
+    tidesapp.py -f file
+
+where file is a JSON file containing either a list of URLs or a list of place names and hints.
+There is no specific limit on the number of URLs or places, tidesapp will query tide data from each.
+
+This script should run on most systems with python, selenium and the Chrome webdriver. There
+are some OS-specific (linux) operations that require running the app's test suite in a linux
+environment (*todo: remove this limitation!*).
+
+The input file is JSON formatted.
+
+Example JSON for operational mode 1 (URLs)..
+
+{
+    "URLs": [
+        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Salisbury/"},
+        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/"},
+        {"URL": "https://www.tideschart.com/United-States/Massachusetts/Essex-County/Rowley/"},
+    ]
+}
+
+Example JSON for operational mode 2 (place names and hints)..
+
+{
+    "URLs": [
+        {"MUNI": "Salisbury, MA", "HINT": "United-States/Massachusetts/Essex-County/Salisbury/"},
+        {"MUNI": "Newburyport, MA", "HINT": "United-States/Massachusetts/Essex-County/Newburyport/"},
+    ]
+}
+"""
+
+import json
+import re
+from datetime import datetime
+from enum import Enum, auto
+from time import sleep
+
+import selenium.common.exceptions
+from selenium import webdriver
+from selenium.webdriver.common.by import By
+from selenium.webdriver.support import expected_conditions as EC
+from selenium.webdriver.support.wait import WebDriverWait
+from datetime_utils import (day2datetime, timestr2time,
+                            date_time_combine)
+from cli_utils import process_command_line
+
+
+class Modes(Enum):
+    """
+    An Enum class to identify which operational mode is currently activated
+
+    Operational Mode 1 (URLs) - Browser navigates directly to a location's tide table
+    Operational Mode 2 (MUNIs) - Browser performs a location search to discover the URL of the tide table
+    """
+    UNKNOWN = auto()
+    URLs = auto()
+    MUNIs = auto()
+
+
+def backoff():
+    """
+    This generator function is used by loops that need to pause for progressively longer times after each
+    iteration. The values returned can be used by the caller as seconds to sleep. The early retries have
+    relatively short pauses. The pauses increase with each iteration until we hit a max value, after which
+    we always return the max.
+
+    Args..
+
+        (none)
+
+    Yields..
+
+        sleep (int) The next sleep value from the sequence of sleep values
+    """
+
+    sleeps = [2, 4, 8, 12, 20, 32, 48] + [60]*1440  # (enough for ~24 hours of retries)
+
+    for sleep in sleeps:
+        yield sleep
+
+
+class TidesApp:
+    """
+    This class implements the primary operations and properties required of the tidesapp application
+    """
+
+    """ Constants """
+
+    BASE_URL = "https://www.tideschart.com"
+
+    # Default URLs for querying tide data for specific location names. This is used only if
+    # no filename is provided on the command line.
+
+    DEFAULT_URLS = [
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Salisbury/"},
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Newburyport/"},
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Rowley/"},
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Crane-Beach/"},
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Wingaersheek-Beach/"},
+     {'URL': BASE_URL + "/United-States/Massachusetts/Essex-County/Rockport/"},
+    ]
+
+    # Municipalities for searching via tideschart's search box. The 'MUNI' data
+    # are the strings entered into tideschart's search box. The 'HINT' data are
+    # used to locate the desired search result from among the myriad results that
+    # are typically returned by tideschart's search tool.
+
+    DEFAULT_MUNIS = [
+     {'MUNI': "Salisbury, MA, USA", 'HINT': "/United-States/Massachusetts/Essex-County/Salisbury/"},
+     {'MUNI': "Newburyport, MA, USA", 'HINT': "/United-States/Massachusetts/Essex-County/Newburyport/"},
+    ]
+
+    # XPATHs
+
+    SEARCHBOX_FORM_XPATH = '//form[@class="app-search"]//input[@id="searchInput"]'
+    SEARCHBOX_CLICK_XPATH = '//form[@class="app-search"]//button[@type="submit"]'
+
+    TOO_MANY_SEARCHES_XPATH = '//*[contains(text(), "Too many search requests")]'
+
+    SEARCH_RESULTS_XPATH = (
+        '//div[@class="search-item"]//*[contains(text(),"HINT")]'
+        + '/parent::div[@class="search-item"]//a'
+    )
+
+    WEEKLY_TABLE_XPATH = (
+        '//table/child::caption[contains(text(), "Tide table for")'
+        + 'and contains(text(), "this week")]/../tbody/tr'
+    )
+
+    # Maximum number of timeouts to wait during a wait-for-web-element loop
+    MAX_TIMEOUTS = 10
+
+    def __init__(self):
+        self.mode = Modes.UNKNOWN
+        self.locations = []
+        self.quickwait = None
+        self.longwait = None
+        self.driver = None
+        self.weekly_tides = None
+        self.attempts = []
+        self.sleep_tracker = []
+
+    def load_user_locations(self, file=None):
+        """
+        Load the list of locations from disk into the tidesapp object.
+
+        Basic sanity checks are performed, after which the list is saved and the method returns.
+
+        Args:
+
+        file - (str) A JSON-formatted file containing a list of URLs, or a list of municipalities
+               and hints. Each URL should be a valid tideschart.com request. Each municipality
+               will be entered into tideschart.com's search box. Each hint is a pattern that
+               uniquely identifies the municipality's result among the many search results.
+
+               If no filename is passed in, a default list is loaded.
+
+        Returns: (nothing)
+
+        Other:
+
+            Once the data are loaded, we detect whether it is for URLs or for municipalities and hints.
+            In the former case we set self.mode to URLs. In the latter case, self.mode is set to MUNIs.
+        """
+
+        if file is None:
+            self.locations = TidesApp.DEFAULT_URLS
+        else:
+            with open(file) as fh:
+
+                data = json.load(fh)
+
+                if 'URLs' in data.keys():
+                    self.mode = Modes.URLs
+                    self.locations = data['URLs']
+                elif 'MUNIs' in data.keys():
+                    self.mode = Modes.MUNIs
+                    self.locations = data['MUNIs']
+                else:
+                    print(f"ERROR: No valid data retrieved from {file}")
+                    raise ValueError
+
+        # Sanity checks
+
+        if self.mode is Modes.URLs:
+            for location in self.locations:
+                if not 'URL' in location.keys():
+                    raise KeyError
+                if not isinstance(location['URL'], str):
+                    raise ValueError
+                if not location['URL'].startswith("https://www.tideschart.com/"):
+                    raise ValueError
+        elif self.mode is Modes.MUNIs:
+            for location in self.locations:
+                if not 'MUNI' in location.keys() or not 'HINT' in location.keys():
+                    raise KeyError
+                if not isinstance(location['MUNI'], str):
+                    raise ValueError
+                if not isinstance(location['HINT'], str):
+                    raise ValueError
+
+    def parse_high_tide_data(self, data):
+        """
+        Parse a single row of tides data. Return a list of high tides.
+
+        Args..
+
+        data (str): A string extracted from the DOM for one row. Contains tide data for only one day.
+
+        Returns..
+
+        tides[]: a list of high tide times (times are expressed as python datetime
+        """
+
+        # Sample data to be parsed:
+        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm'
+        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm'
+        #
+        # Notes..
+        #
+        # (1) The web page indicates high tide with unicode character
+        #     up triangle, and low tide with down triangle.
+        #
+        # (2) It is possible to have only three tides in a day!
+
+        # The following regex will parse any data adhering to the format in the above examples..
+
+        pattern = re.compile(
+         "^\s*" +
+         "(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+" +
+         "(?P<dayno>\d+)\s+" +
+         "(?P<tide1_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide1_hilo>(?:▲|▼))\s+(?P<tide1_height>\d+(?:\.\d+|))\s*ft\s+" +
+         "(?P<tide2_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide2_hilo>(?:▲|▼))\s+(?P<tide2_height>\d+(?:\.\d+|))\s*ft\s+" +
+         "(?P<tide3_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide3_hilo>(?:▲|▼))\s+(?P<tide3_height>\d+(?:\.\d+|))\s*ft\s+" +
+         "(?:(?P<tide4_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide4_hilo>(?:▲|▼))\s+(?P<tide4_height>\d+(?:\.\d+|))\s*ft\s+|)" +
+         "▲\s*(?P<sunrise>\d+:\d\d\s*(?:am|pm))\s+" +
+         "▼\s*(?P<sunset>\d+:\d\d\s*(?:am|pm))\s*$"
+        )
+
+        # Get rid of all newlines in the data stream, they may be safely ignored in this method
+        data = re.sub('\n', ' ', data)
+
+        # Parse the row's data..
+
+        matched = re.match(pattern, data)
+
+        if not matched:
+            print(f"ERROR: Tide data not parsed: {data}")
+            raise ValueError
+
+        # Convert the day to a datetime
+        this_day = day2datetime(matched.group('dayno'))
+
+        # Assemble the list of tides
+        this_day_high_tides = []
+        for timestr, hilo in [
+            (matched.group('tide1_time'), matched.group('tide1_hilo')),
+            (matched.group('tide2_time'), matched.group('tide2_hilo')),
+            (matched.group('tide3_time'), matched.group('tide3_hilo')),
+            (matched.group('tide4_time'), matched.group('tide4_hilo'))
+        ]:
+            # Check if this tide data is for a high tide or low tide
+            if hilo == '▲':
+                # ok, it is for a high tide! Continue processing..
+
+                # Convert time (e.g., "3:32 am") to a datetime object
+                this_high_tide_time = timestr2time(timestr)
+                # Combine with the day's datetime
+                this_high_tide_datetime = date_time_combine(
+                    this_day, this_high_tide_time)
+                # Append the datetime
+                this_day_high_tides.append(this_high_tide_datetime)
+
+        if len(this_day_high_tides) < 1:
+            print(f"ERROR: No high tide data found for: {data}")
+            raise ValueError
+        if len(this_day_high_tides) > 2:
+            print(f"ERROR: Too many high tides found for: {data}")
+            raise ValueError
+
+        return this_day_high_tides
+
+    def get_weekly_tides(self, URL):
+        """
+        Retrive tide data for one location. Return a list of tides for the upcoming week.
+
+        This method is only for operational mode 1.
+
+        This method navigates the browser to a URL which renders weekly tide data for one
+        particular location.
+
+        The table of tide data is located in the DOM and, for each day in the table, the
+        tide data are extracted and saved to the weekly_tides object.
+
+        The browser object (self.driver) is assumed to have already been created.
+
+        Args..
+
+        URL (str): A URL, starting with 'https://www.tideschart.com/' that renders a
+                   weekly tide table for one location.
+
+        Returns..
+
+        weekly_tides, a list of high tides over one week for a particular location
+        """
+
+        self.driver.get(URL)
+        self.longwait.until(EC.presence_of_element_located((By.XPATH, TidesApp.WEEKLY_TABLE_XPATH)))
+        weekly_tides_dom = self.driver.find_elements_by_xpath(TidesApp.WEEKLY_TABLE_XPATH)
+
+        if not len(weekly_tides_dom) == 7:
+            raise ValueError
+
+        weekly_tides_one_location = []
+
+        for i in range(7):
+            weekly_tides_one_location += self.parse_high_tide_data(weekly_tides_dom[i].text)
+
+        return weekly_tides_one_location
+
+    def get_weekly_tides_via_search_box(self, municipality):
+        """
+        Retrive tide data for one location. Return a list of tides for the upcoming week.
+
+        This method is only for operational mode 2.
+
+        This version interracts with the search box at www.tideschart.com in order to
+        bring up the tide chart for the requested location.
+
+        The table of tide data is located in the DOM and, for each day in the table, the
+        tide data are extracted and saved to the weekly_tides object.
+
+        The browser object (self.driver) is assumed to have already been created.
+
+        NOTE: The site (tideschart.com) implements a throttling mechanism which prevents us
+        from issuing too many searches in a certain time period. This method contains a
+        while-loop which will retry the search several times. Eventually one of our searches
+        succeeds.
+
+        Args..
+
+        municipality (dict): A dictionary with the following keys..
+
+            ['MUNI'] (str): The name of a location to be entered in the search box at
+                            www.tideschart.com. Format is "TownOrCity, State". Can also be set
+                            to a zip code.
+
+            ['HINT'] (str): A pattern used to locate the location's link in the search results.
+
+        Returns..
+
+        weekly_tides, a list of high tides over one week for a particular location
+        """
+
+        # Make an XPATH string from the template (TidesApp.SEARCH_RESULTS_XPATH). The template contains
+        # the string 'HINT' which needs to be replaced with the hint supplied by user via the input file.
+
+        search_results_xpath = re.sub('HINT', municipality['HINT'], TidesApp.SEARCH_RESULTS_XPATH)
+
+        this_result = None
+        self.timeouts = self.too_many_searches_errors = 0
+        still_searching = True
+        sleeper = backoff()
+
+        while still_searching and self.timeouts < TidesApp.MAX_TIMEOUTS:
+
+            self.driver.get(TidesApp.BASE_URL)
+            searchbox_form = self.longwait.until(EC.presence_of_element_located((By.XPATH, TidesApp.SEARCHBOX_FORM_XPATH)))
+            searchbox_form.send_keys(municipality['MUNI'])
+            searchbox_click = self.longwait.until(EC.presence_of_element_located((By.XPATH, TidesApp.SEARCHBOX_CLICK_XPATH)))
+            searchbox_click.click()
+
+            try:
+                self.attempts.append([municipality['MUNI'], datetime.now()])
+                this_result = self.quickwait.until(EC.element_to_be_clickable((By.XPATH, search_results_xpath)))
+            except (selenium.common.exceptions.TimeoutException, TimeoutError):
+                self.timeouts += 1
+                too_many = self.quickwait.until(EC.presence_of_element_located((By.XPATH, TidesApp.TOO_MANY_SEARCHES_XPATH)))
+                if too_many is not None:
+                    self.too_many_searches_errors += 1
+                sleepval = next(sleeper)
+                self.sleep_tracker.append([municipality['MUNI'], sleepval])
+                sleep(sleepval)
+            finally:
+                if this_result is not None:
+                    still_searching = False
+
+        if still_searching:
+            print("ERROR: Unable to find search results")
+            raise TimeoutError
+
+        this_result.click()
+
+
+    def mainapp(self):
+        """
+        This method is the main entry point for the app. Major tasks
+        include..
+
+        Parsing the user's command line
+        Loading the user's location URLs into the app
+        Initializing the webdriver
+        Calling the weekly tides retriever for each location
+        """
+
+        file = process_command_line()
+        self.load_user_locations(file)
+        self.driver = driver = webdriver.Chrome()
+        self.quickwait = WebDriverWait(driver, 5)
+        self.longwait = WebDriverWait(driver, 30)
+        self.weekly_tides = {}
+        if self.mode is Modes.URLs:
+            for URL in self.locations:
+                self.weekly_tides[URL['URL']] = self.get_weekly_tides(URL['URL'])
+        elif self.mode is Modes.MUNIs:
+            for X in self.locations:
+                self.weekly_tides[X['MUNI']] = self.get_weekly_tides_via_search_box(X)
+
+        # TODO: Do something with the data!!!
+
+        # That is all for now
+        driver.close()
+
+
+if __name__ == '__main__':
+    TidesApp().mainapp()
