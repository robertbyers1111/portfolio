
## Robert Byers
### QA Automation Engineer, SDET, Test Automation

------------

Note: (Aug. 2022) This portfolio is a work-in-progress. Appologies if it seems minimal at this time. I am working dilligently to get additional quality work uploaded in a timely fashion!

------------

#### [tidesapp](https://github.com/robertbyers1111/portfolio/tree/master/tides)

tidesapp is an application that gathers high tide data for a number of locations and reports the results to the user. This is a new app I started on 8/23/2022. My intention is that it will grow over the next days or weeks to encompass some additional features. These are some of the skills this app highlights..

- Test design and implementation
- Python
- pytest
- Selenium
- XPATH (Finding and interracting with DOM elements using XPATH)
- JSON parsing
- Command line parsing with *argparse*
- Regular expressions (advanced)
- Generator (yield) functions

The app itself should run from most any system with python, selenium and the Chrome webdriver. There are some OS-specific (linux) operations that require running the app's test suite in a linux environment (*todo: remove this limitation!*).

I selected tideschart.com for retrieving tide data. It supports retrieval of weekly tide data for most US beaches via a simple URL formulation. For example, to retrieve the current week's tide data for Newburyport, MA, navigating a browser to the following URL is sufficient..

        https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/

The app is launched from a command line with the following syntax..

`tidesapp -f file`

..where *file* is a JSON file containing a list of URLs. There is no specific limit on the number of URLs, tidesapp will query tide data from each.

The source code for the app itself is in the tides/tidesapp folder. The code for all pytests is in tides/tests.

|  Folder | File   | Description   |
| ------------ | ------------ | ------------ |
| tides/tidesapp   | tidesapp.py  | This is the main application source  |
| tides/tidesapp   | cli_utils.py  | Methods for parsing tidesapp's command line  |
| tides/tidesapp   | datetime_utils.py  | Methods for converting dates and times from the rendered DOM elements into python datetime constructs  |
| tides/tests  | tests_tidesapp.py  | pytest suite for the main application  |
| tides/tests  | tests_cli_utils.py  | pytest unit testing for the CLI utilities  |
| tides/tests  | tests_datetime_utils.py  | pytest unit testing for the datetime utilities  |
| tides/tests  | sample_input.json  | Persistent test input  |
| tides  | setup.cfg  | Sets *pythonpath*, etc.  |

