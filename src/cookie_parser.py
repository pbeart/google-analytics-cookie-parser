"""
Provide helper functions and classes for parsing cookies and GA cookie
info from supported browsers
"""

import sqlite3
from urllib.request import pathname2url
import time

def create_ga_list(values, length):
    """Return the list of values, padded to specified length with '<not found>'"""

    template = ["<not found>"] * length

    for index, element in enumerate(values[:length]):
        template[index] = element
    return template

def try_parse_int(number):
    """
    Try to parse a string or other to an int, or return the string
    if not possible
    """
    try:
        return int(number)
    except (ValueError, TypeError) as _:
        return number

def try_parse_epoch_datetime(datetime, time_unit="seconds"):
    """
    Try to parse a string containing an epoch datetime to a nicely formatted
    output, or return the string if not possible
    """
    try:
        converted = float(datetime) / (1.0 if time_unit == "seconds" else 1000.0)
        try:
            return time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(converted))
        except (ValueError, OSError) as _:
            return datetime
    except ValueError:
        return datetime # Could not be parsed into a float


def ga_parse(name, value):
    """
    Parse a GA cookie and return a dict with the specific cookie type's info
    """
    if not "." in value:
        # If the value is nothing like we expect, we don't have any valid data
        # so we should just pad the empty data to the right number of Nones
        elements = []
    else:
        elements = value.split(".")

    if name == "_ga":
        # Returns dots in domain, clientID, first time site visited
        padded_elements = create_ga_list(elements, 4)
        return {"value_dots_in_domain": padded_elements[0],
                "value_client_identifier": padded_elements[2],
                "time_first_visit": try_parse_epoch_datetime(padded_elements[3])}
    elif name == "__utma":
        # Returns  domain hash, visitor identifier, cookie creation time,
        #          time of 2nd most recent visit, time of most recent visit,
        #          total number of visits
        padded_elements = create_ga_list(elements, 6)
        return {"value_domain_hash": padded_elements[0],
                "value_visitor_identifier": padded_elements[1],
                "time_2nd_most_recent_visit": try_parse_epoch_datetime(padded_elements[3]),
                "time_most_recent_visit": try_parse_epoch_datetime(padded_elements[4]),
                "count_visits_utma": padded_elements[5]}
    elif name == "__utmb":
        # Returns [domain hash, page views in current session, outbound link clicks
        #          (worth noting that this is 10-actual value),
        #          time that current session started]
        padded_elements = create_ga_list(elements, 4)
        return {"value_domain_hash": padded_elements[0],
                "count_session_pageviews": padded_elements[1],
                "count_outbound_clicks": padded_elements[2],
                "time_session_start": try_parse_epoch_datetime(padded_elements[3])}
    elif name == "__utmz":
        # Returns [domain hash, last update time, number of visits,
        #          number of different types of visits (campaigns),
        #          source used to access site, adwords campaign name,
        #          access method, keyword used to find site]
        padded_elements = create_ga_list(elements, 8)
        return {"value_domain_hash": padded_elements[0],
                "time_last_update": try_parse_epoch_datetime(padded_elements[1]),
                "count_visits_utmz": padded_elements[2],
                "count_visits_campaings": padded_elements[3],
                "value_visit_source": padded_elements[4],
                "value_adwords_campaign": padded_elements[5],
                "value_access_method": padded_elements[6],
                "value_search_term": padded_elements[7]}

def ga_generate_table(parsed_rows, cookie_name):
    """
    Converts a list of (cookie host, cookie creation time, cookie value) to a
    csv-able list of dicts
    """

    headers = {
        "_ga":    [["First visit time", "time_first_visit"],
                   ["Client Identifier", "value_client_identifier"]],

        "__utma": [["Total visits", "count_visits_utma"],
                   ["Most recent visit", "time_most_recent_visit"],
                   ["Second most recent visit", "time_2nd_most_recent_visit"],
                   ["Visitor Identifier", "value_visitor_identifier"]],

        "__utmb": [["Page views in current session", "count_session_pageviews"],
                   ["Time current session started", "time_session_start"],
                   ["10 - Outbound link clicks", "count_outbound_clicks"]],

        "__utmz": [["Total visits", "count_visits_utmz"],
                   ["Source used to access site", "value_visit_source"],
                   ["Keyword used to find site", "value_search_term"]]
    }

    current_headers = ["Cookie host", cookie_name+" value", "Cookie creation time"]
    current_headers += [pair[0] for pair in headers[cookie_name]]

    output = [current_headers]

    for host, creation_time, value in parsed_rows:

        parsed = ga_parse(cookie_name, value)

        values = [parsed[pair[1]] for pair in headers[cookie_name]]

        columns = [host, value, try_parse_epoch_datetime(creation_time)] + values

        output.append(columns)

    return output

def ga_summary(inp):
    """
    Returns a summary dict of the ga cookie info, taking list inp of
    format [(ga cookie name, cookie value), ...]
    """
    keys = {
        "time_first_visit": "_ga", # First visit (from _ga)
        "time_most_recent_visit": "__utma", # Most recent visit (from __utma)
        "time_2nd_most_recent_visit": "__utma", # 2nd most recent visit (from __utma)
        "count_visits_utma": "__utma", # Number of visits (from __utma)
        "count_visits_utmz": "__utmz", # Number of visits (from __utmz)
        "time_session_start": "__utmb", # Time most recent session was started (from __utmb)
        "count_session_pageviews": "__utmb", # Time most recent session was started (from __utmb)
        "value_search_term": "__utmz", # Search keyword used to find site (from __utmz)
        "value_visit_source": "__utmz", # Source of site access (from __utmz)
        "count_outbound_clicks": "__utmb", # 10 - Number of clicks to external links (from __utmb)
        "value_client_identifier": "_ga", # Client identifier (from _ga)
        "value_visitor_identifier": "__utma" # Visitor identifier (from __utma)
        }

    output = {}

    for row in inp:
        for name in keys:
            if row[0] == keys[name]: # If this row name corresponds to the source of an artifact
                data = ga_parse(row[0], row[1]) # Parse this row
                output[name] = data[name]

    return output

def get_cookie_fetcher(browser, *args, **kwargs):
    """
    Returns the appropriate CookieFetcher subclass for the given
    browser shortname
    """

    if browser == "firefox.3+":
        return Firefox3Fetcher(*args, **kwargs)

class CookieFetcher:
    """
    Template CookieFetcher for browser fetchers to inherit from
    """

    def __init__(self, filepath):
        """
        Should be used to prepare target browser artifact to be
        accessed and read
        """

    def get_domains(self):
        """
        Return a list of unique domains for which GA cookies are found
        """

    def get_cookie_count(self):
        """
        Return the total number of GA cookies found
        """

    def get_cookies(self, cookie_name):
        """
        Return a list of [(cookie host, creation time, value), ...]
        """

    def get_domain_info(self, domain):
        """
        Return a ga_summary-style output dict of domain specific cookie
        information
        """

class Firefox3Fetcher(CookieFetcher):
    """
    CookieFetcher for Firefox 3+
    """
    def __init__(self, filepath, cookie_names=None):
        # pylint: disable=super-init-not-called
        cookie_names = ["_ga", "_utma", "_utmb", "_utmz"] if cookie_names is None else cookie_names

        # Use a path uri to prevent sqlite from creating the
        # database, allowing us to check whether the database
        # can be read without automatically creating it
        path_uri = "file:{}?mode=rw".format(pathname2url(filepath))

        self.cookie_names = cookie_names

        self.error = None

        # Test file can actually be opened
        try:
            self.conn = sqlite3.connect(path_uri, uri=True)
        except sqlite3.OperationalError:
            self.error = "The selected file could not be opened"
            return

        # Test that it is a valid database, and that the moz_cookies
        # table exists
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT name FROM sqlite_master\
                                 WHERE type='table' AND name='moz_cookies';")
            # moz_cookies table not present
            if self.cursor.fetchone() is None:
                self.error = "The selected file was a valid database\
but did not have the moz_cookies table"
                return

        except sqlite3.DatabaseError:
            self.error = "The selected file is not a valid sqlite3 database"
            return

    def get_domains(self):
        # Create a list with the correct number of ?s to act as a parameter
        # substition template for the SQLite query
        question_marks = ",".join(["?"]*len(self.cookie_names))
        # Use the question_marks list to create the query
        self.cursor.execute("SELECT DISTINCT host FROM moz_cookies WHERE \
name IN ({})".format(question_marks),
                            self.cookie_names)

        results = self.cursor.fetchall()
        return [result[0] for result in results]

    def get_domain_info(self, domain):
        # Create a list with the correct number of ?s to act as a parameter
        # substition template for the SQLite query
        question_marks = ",".join(["?"]*len(self.cookie_names))
        # Use the question_marks list to create the query
        self.cursor.execute("SELECT name,value FROM moz_cookies WHERE \
name IN ({}) AND host = ?".format(question_marks),
                            self.cookie_names+[domain])
        return ga_summary(self.cursor.fetchall())

    def get_cookies(self, cookie_name):
        self.cursor.execute("SELECT host, creationTime, value FROM moz_cookies WHERE name = ?",
                            [cookie_name])

        return ga_generate_table(self.cursor.fetchall(), cookie_name)

    def get_cookie_count(self):
        # Create a list with the correct number of ?s to act as a parameter
        # substition template for the SQLite query
        question_marks = ",".join(["?"]*len(self.cookie_names))
        # Use the question_marks list to create the query
        self.cursor.execute("SELECT COUNT(host) FROM moz_cookies WHERE \
name IN ({})".format(question_marks),
                            self.cookie_names)

        results = self.cursor.fetchone()
        return results[0]
