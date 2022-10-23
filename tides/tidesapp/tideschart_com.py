#!/bin/env python3

import re
import json
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from datetime_utils import day2datetime, timestr2time, date_time_combine
from json_utils import check_dict_keys


class SeleniumObject:
    """
    A class for storing selenium-specific attributes
    """

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.quick_wait = WebDriverWait(self.driver, 5)
        self.long_wait = WebDriverWait(self.driver, 30)

    def get_attrs(self):
        return self.driver, self.quick_wait, self.long_wait


class TideschartDotCom:

    """ Constants """

    BASE_URL = "https://www.tideschart.com"

    # XPATHs for navigating www.tideschart.com

    SEARCHBOX_FORM = '//form[@class="app-search"]//input[@id="searchInput"]'
    SEARCHBOX_CLICK = '//form[@class="app-search"]//button[@type="submit"]'

    TOO_MANY_SEARCHES = '//*[contains(text(), "Too many search requests")]'

    SEARCH_RESULTS = (
        '//div[@class="search-item"]//*[contains(text(),"HINT")]'
        + '/parent::div[@class="search-item"]//a'
    )

    WEEKLY_TABLE = (
        '//table/child::caption[contains(text(), "Tide table for")'
        + 'and contains(text(), "this week")]/../tbody'
    )

    # Maximum number of timeouts to wait during a wait-for-web-element loop
    MAX_TIMEOUTS = 10

    def __init__(self, file):
        self.file = file
        self.selenium_obj = SeleniumObject()
        self.timeouts = 0
        self.too_many_searches_errors = 0
        self.attempts = []
        self.sleep_tracker = []

    def load_URLs(self, file):
        """
        Load the user's requested URLs from the input JSON file

        Args..

            file - (str) A JSON-formatted file containing a list of URLs, each of which loads the tide data for one location

        Returns..

            URLs - (list of strings) Each string is a URL of the form "https://www.tideschart.com/Country/State/County/Locality/"
        """

        if file is None:
            print("\nERROR: input filename must not be 'None'")
            raise ValueError
        else:
            with open(file) as fh:
                json_data = json.load(fh)

                # Sanity checks. The input should have only one outer json key ('URLs') which contains a list. The
                # list contains items that are dictionaries with only one key ('URL')
                check_dict_keys(json_data, 1, ['URLs'])
                for row in json_data['URLs']:
                    check_dict_keys(row, 1, ['URL'])
                    if not row['URL'].startswith("https://www.tideschart.com/"):
                        print(f"\nERROR: {row['URL']} does not start with https://www.tideschart.com/")
                        raise ValueError

        # Extract the URLs. Place them in a list to be returned.
        URLs = []
        for row in json_data['URLs']:
            URLs.append(row['URL'])

        return URLs

    def load_tides_via_URL(self, file):
        """
        Navigate a browser to various URLs. Extract weekly tides data for the DOM retrieved for each URL.

        Args..

            file - (str) A JSON-formatted file containing a list of URLs, each of which loads the tide data for one location

        Returns..

            weekly_tides_all_locations (dict) Keys are each of the URLs. Values are lists of high tide times for the upcoming week.

        """

        weekly_tides_all_locations = {}

        URLs = self.load_URLs(file)

        driver, quick_wait, long_wait = self.selenium_obj.get_attrs()

        for URL in URLs:
            driver.get(URL)
            long_wait.until(ec.presence_of_element_located((By.XPATH, TideschartDotCom.WEEKLY_TABLE)))
            weekly_tides_dom = driver.find_element(By.XPATH, TideschartDotCom.WEEKLY_TABLE)

            if not len(weekly_tides_dom) == 7:
                raise ValueError

            weekly_tides_one_location = []

            # When this loop finishes, we will have a list of 7 elements, containing high tides data for one week at one location
            for i in range(7):
                # Each iteration parses the high tide data for one day at one location
                weekly_tides_one_location += self.parse_high_tide_data(weekly_tides_dom[i].text)

            # The data for an entire week at one location is then stored in a dictionary, keyed by the location's URL (with
            # https:// removed). The location's weekly tide data become the dictionary's value.

            key = re.sub("https://", "", URL)
            weekly_tides_all_locations[key] = weekly_tides_one_location

        # Now we have a dictionary for all locations. Locations are the dictionary keys and weekly tide data are the dictionary values.

        return weekly_tides_all_locations

    def load_searches(self, file):
        """
        Load the municipality data from user's input file, then use Selenium to search for each municipality via
        tideschart.com's search box, and return a list containing the SEARCH tuples (location & hint)

        Args..

            file - (str) A JSON-formatted file containing a list of municipalities and hints. The municipality is used
            as the search term in tideschart.com's search box. The hint is used to locate the corresponding result from
            among the *many* (!) search results that tideschart.com tends to present after a search.

        Returns..

            searches - (list of tuples) Each tuple is a pair of strings. The first string is the search term to be
            keyed into the search field at tideschart.com. The second string is the 'hint' to be used to locate the
            desired result from among the search results.
        """

        if file is None:
            print("\nERROR: input filename must not be 'None'")
            raise ValueError
        else:
            with open(file) as fh:
                json_data = json.load(fh)

                # Sanity checks. The input should have only one outer json key ('URLs') which contains a list. The
                # list contains items that are dictionaries with only one key ('URL')
                check_dict_keys(json_data, 1, ['SEARCHES'])
                for row in json_data['SEARCHES']:
                    check_dict_keys(row, 2, ['SEARCH', 'HINT'])

        # Extract the search locations and hints. Place them in a list to be returned
        searches = []
        for row in json_data['SEARCHES']:
            searches.append((row['SEARCH'], row['HINT']))

        return searches

    def load_tides_via_search_box(self, location, hint):
        """
        Use tideschart.com's search box to find tides data for one location. Return a list of tides
        for the upcoming week.

        This method is operational mode 2.

        The table of tide data is located in the DOM and, for each day in the table, the tide data
        are extracted and saved to the weekly_tides object.

        The browser object (self.driver) is assumed to have already been created.

        NOTE: The site (tideschart.com) implements a throttling mechanism which prevents us
        from issuing too many searches in a certain time period. This method contains a
        while-loop which will retry the search several times. Eventually one of our searches
        succeeds.

        Args..

            location (str): The name of a location to be entered in the search box at www.tideschart.com.
                            Format is "TownOrCity, State". Can also be set to a zip code.

            hint (str): A pattern used to locate the location's link in the search results.

        Returns..

            weekly_tides (list of str), a list of high tides over one week for a particular location
        """

        # Construct an XPATH from the template in SEARCH_RESULTS. This template contains 'HINT'
        # which will be replaced with the hint passed in as an argument.

        search_results_xpath = re.sub('HINT', hint, TideschartDotCom.SEARCH_RESULTS)

        this_result = None
        self.timeouts = self.too_many_searches_errors = 0
        still_searching = True
        sleeper = backoff()

        while still_searching and self.timeouts < TideschartDotCom.MAX_TIMEOUTS:

            self.driver.get(TideschartDotCom.BASE_URL)
            searchbox_form = self.long_wait.until(ec.presence_of_element_located((By.XPATH, TideschartDotCom.SEARCHBOX_FORM)))
            searchbox_form.send_keys(location)
            searchbox_click = self.long_wait.until(ec.presence_of_element_located((By.XPATH, TideschartDotCom.SEARCHBOX_CLICK)))
            searchbox_click.click()

            try:
                self.attempts.append([location, datetime.now()])
                this_result = self.quick_wait.until(ec.element_to_be_clickable((By.XPATH, search_results_xpath)))
            except (selenium.common.exceptions.TimeoutException, TimeoutError):
                self.timeouts += 1
                warning_too_many = self.quick_wait.until(ec.presence_of_element_located((By.XPATH, TideschartDotCom.TOO_MANY_SEARCHES)))
                if warning_too_many is not None:
                    self.too_many_searches_errors += 1
                sleep_val = next(sleeper)
                self.sleep_tracker.append([location, sleep_val])
                sleep(sleep_val)
            finally:
                if this_result is not None:
                    still_searching = False

        if still_searching:
            print("ERROR: Unable to find search results")
            raise TimeoutError

        this_result.click()

        # TODO: Assemble a list of URLs and then leverage load_tides_via_URL
        print()

    def parse_high_tide_data(self, data):
        """
        Parse a single row of tides data. Return a list of high tides.

        Args..

            data (str): A string extracted from the DOM for one row. Contains tide data for only one day.

        Returns..

            tides (list): Times of a day's high tides, stored as python datetime.
        """

        # Sample data to be parsed:
        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft 9:17pm ▲ 7.55 ft ▲ 5:57am ▼ 7:35pm'
        # 'Mon 22 3:36am ▼ 0.98 ft 9:09am ▲ 6.56 ft 3:41pm ▼ 1.64 ft ▲ 5:57am ▼ 7:35pm'
        #
        # Notes..
        #
        # (1) The web page indicates high tide with unicode character
        #     up triangle, and low tide with down triangle.
        #
        # (2) It is possible to have only three tides in a day!

        # The following regex will parse any data adhering to the format in the above examples..

        pattern = re.compile(
         r"^\s*" +
         r"(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+" +
         r"(?P<day_no>\d+)\s+" +
         r"(?P<tide1_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide1_hilo>[▲▼])\s+(?P<tide1_height>\d+(?:\.\d+|))\s*ft\s+" +
         r"(?P<tide2_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide2_hilo>[▲▼])\s+(?P<tide2_height>\d+(?:\.\d+|))\s*ft\s+" +
         r"(?P<tide3_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide3_hilo>[▲▼])\s+(?P<tide3_height>\d+(?:\.\d+|))\s*ft\s+" +
         r"(?:(?P<tide4_time>\d+:\d\d\s*(?:am|pm))\s+(?P<tide4_hilo>[▲▼])\s+(?P<tide4_height>\d+(?:\.\d+|))\s*ft\s+|)" +
         r"▲\s*(?P<sunrise>\d+:\d\d\s*(?:am|pm))\s+" +
         r"▼\s*(?P<sunset>\d+:\d\d\s*(?:am|pm))\s*$"
        )

        # Get rid of all newlines in the data stream, they may be safely ignored in this method
        # PROBLEM: here 'data' is the dictionary but the re.sub() expects it to be a row of data from a selenium operation
        tide_data_fr_dom = re.sub('\n', ' ', data['URL'])
        # TODO: check: data is a dict???     ^^^^^^^^^^^

        # Parse the row's data..

        matched = re.match(pattern, tide_data_fr_dom)

        if not matched:
            print(f"\nERROR: Tide data not parsed: {tide_data_fr_dom}")
            raise ValueError

        # Convert the day to a datetime
        this_day = day2datetime(matched.group('day_no'))

        # Assemble the list of tides
        this_day_high_tides = []
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
                this_high_tide_time = timestr2time(timestr)
                # Combine with the day's datetime
                this_high_tide_datetime = date_time_combine(
                    this_day, this_high_tide_time)
                # Append the datetime
                this_day_high_tides.append(this_high_tide_datetime)

        if len(this_day_high_tides) < 1:
            print(f"\nERROR: No high tide data found for: {tide_data_fr_dom}")
            raise ValueError
        if len(this_day_high_tides) > 2:
            print(f"\nERROR: Too many high tides found for: {tide_data_fr_dom}")
            raise ValueError

        return this_day_high_tides
