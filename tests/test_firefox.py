"""
Test Firefox 3+ specific parsing functionality
"""

import pytest

import cookie_parser

def test_summary():
    cookies = ["_ga", "__utma", "__utmb", "__utmz"]
    parser = cookie_parser.get_cookie_fetcher("firefox.3+",
                                              "tests\\firefox.sqlite",
                                              cookies)

    summary = parser.get_domain_info(".testdomain.com")

    # The values of the cookies in firefox.sqlite are such that
    # get_domain_info should return:

    expected_output = {"value_visitor_identifier": "2100671096",
                       "time_most_recent_visit": "2019-09-20 17:31:57Z",
                       "time_2nd_most_recent_visit": "2019-09-20 10:10:16Z"}


    print(summary)