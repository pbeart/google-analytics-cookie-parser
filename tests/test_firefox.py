"""
Test Firefox 3+ specific parsing functionality
"""

import pytest

import cookie_parser

def validate_keys(selection, values):
    """
    Checks that all of the keys which selection has have the same
    values as those keys in values
    """
    for key in selection:
        assert(key in values)
        assert(values[key] == selection[key])

def test_summary():
    cookies = ["_ga", "__utma", "__utmb", "__utmz"]
    parser = cookie_parser.get_cookie_fetcher("firefox.3+",
                                              "tests\\firefox.sqlite",
                                              cookies)

    summary = parser.get_domain_info(".testdomain.com")

    # The values of the cookies in firefox.sqlite are such that
    # get_domain_info should return:

    expected_output_utma = {"value_visitor_identifier": "2100671096",
                            "time_2nd_most_recent_visit": "2019-09-20 17:31:57Z",
                            "time_most_recent_visit": "2019-09-20 17:31:57Z",
                            "count_visits_utma":"1"}

    validate_keys(expected_output_utma, summary)

    expected_output_utmb = {"count_session_pageviews": "1",
                            "count_outbound_clicks": "10",
                            "time_session_start":"2019-09-20 17:31:57Z"}

    validate_keys(expected_output_utmb, summary)
    
    expected_output_utmz = {"count_visits_utmz": "1",
                            "value_visit_source": "visit_source",
                            "value_access_method": "access_method",
                            "value_search_term": "search_query"}

    validate_keys(expected_output_utmz, summary)

    expected_output_ga = {"value_client_identifier": "974259038",
                          "time_first_visit": "2019-08-30 21:40:32Z"}

    validate_keys(expected_output_ga, summary)