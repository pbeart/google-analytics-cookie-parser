"""
Provides functions to help with parsing GA cookies
"""

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

def try_parse_kvp(instring, key):
    """
    Try to parse a GA-style key-value pair string and retrieve the specified key,
    returning <not found> if the given key is not found or if the string could
    not be parsed
    """
    key_value_pairs = instring.split("|")
    key_dict = {pair.split("=")[0]: pair.split("=")[1] for pair in key_value_pairs if "=" in pair}
    return key_dict.get(key, "<not found>")

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
        padded_elements = create_ga_list(elements, 5)
        return {"value_domain_hash": padded_elements[0],
                "time_last_update": try_parse_epoch_datetime(padded_elements[1]),
                "count_visits_utmz": padded_elements[2],
                "count_visits_campaigns": padded_elements[3],
                "value_visit_source": try_parse_kvp(padded_elements[4], "utmcsr"),
                "value_adwords_campaign": try_parse_kvp(padded_elements[4], "utmccn"),
                "value_access_method": try_parse_kvp(padded_elements[4], "utmcmd"),
                "value_search_term": try_parse_kvp(padded_elements[4], "utmctr")}

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
        "value_visitor_identifier": "__utma", # Visitor identifier (from __utma)
        "value_access_method": "__utmz" # Access method (from __utmz)
        }

    output = {}

    for row in inp:
        for name in keys:
            if row[0] == keys[name]: # If this row name corresponds to the source of an artifact
                data = ga_parse(row[0], row[1]) # Parse this row
                output[name] = data[name]

    return output
