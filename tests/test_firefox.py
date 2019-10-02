"""
Integration tests designed to make sure that the output of the tool is
forensically sound, *not* to unit test.
"""

import os.path

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

def test_export():
    cookies = {"_ga":[['Cookie host', '_ga value', 'Cookie creation time', 'First visit time', 'Client Identifier'],
                      ['.testdomain.com', 'GA1.2.974259038.1567201232', '2019-09-20 17:31:56Z', '2019-08-30 21:40:32Z', '974259038']],
              
               "__utma":[['Cookie host', '__utma value', 'Cookie creation time', 'Total visits', 'Most recent visit', 'Second most recent visit', 'Visitor Identifier'],
                         ['.testdomain.com', '267265176.2100671096.1568974216.1569000717.1569000717.1', '2019-09-20 17:31:56Z', '1', '2019-09-20 17:31:57Z', '2019-09-20 17:31:57Z', '2100671096']],
             
               "__utmb":[['Cookie host', '__utmb value', 'Cookie creation time', 'Page views in current session', 'Time current session started', '10 - Outbound link clicks'],
                         ['.testdomain.com', '267265176.1.10.1569000717', '2019-09-20 17:31:56Z', '1', '2019-09-20 17:31:57Z', '10']],
             
               "__utmz":[['Cookie host', '__utmz value', 'Cookie creation time', 'Total visits', 'Source used to access site', 'Keyword used to find site'],
                         ['.testdomain.com', '267265176.1569000717.1.1.utmcsr=visit_source|utmccn=adwords_campaign|utmcmd=access_method|utmctr=search_query', '2019-09-20 17:31:56Z', '1', 'visit_source', 'search_query']]}

    # os.path.join must be used because the Travis testing environment
    # could be WIndows or Linux

    parser = cookie_parser.get_cookie_fetcher("firefox.3+",
                                              os.path.join("tests","firefox.sqlite"),
                                              list(cookies.keys()))

    assert(parser.error == None)

    for cookie_name in cookies:
        table = parser.get_cookies(cookie_name)
        assert(table==cookies[cookie_name])

def test_summary():
    cookies = {"_ga":   {"value_client_identifier": "974259038",
                         "time_first_visit": "2019-08-30 21:40:32Z"},

               "__utma":{"value_visitor_identifier": "2100671096",
                         "time_2nd_most_recent_visit": "2019-09-20 17:31:57Z",
                         "time_most_recent_visit": "2019-09-20 17:31:57Z",
                         "count_visits_utma":"1"},

               "__utmb":{"count_session_pageviews": "1",
                         "count_outbound_clicks": "10",
                         "time_session_start":"2019-09-20 17:31:57Z"},

               "__utmz":{"count_visits_utmz": "1",
                         "value_visit_source": "visit_source",
                         "value_access_method": "access_method",
                         "value_search_term": "search_query"}}

    # os.path.join must be used because the Travis testing environment
    # could be WIndows or Linux

    parser = cookie_parser.get_cookie_fetcher("firefox.3+",
                                              os.path.join("tests","firefox.sqlite"),
                                              list(cookies.keys()))

    assert(parser.error == None)

    summary = parser.get_domain_info(".testdomain.com")

    for cookie_name in cookies:
        validate_keys(cookies[cookie_name], summary)