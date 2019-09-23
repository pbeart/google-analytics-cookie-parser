# Template for the domain info panel. We use format to substitute the parsed
# domain cookie values in, meaning that the {format names} are actually the
# keys of the return value of cookie_parser.ga_parse
DOMAIN_INFO_TEMPLATE = """Domain Info: (source)
First visit: {time_first_visit} (_ga)
Most recent visit: {time_most_recent_visit} (__utma)
Second most recent visit: {time_2nd_most_recent_visit} (__utma)
Number of visits: {count_visits_utma} (__utma)
Number of visits: {count_visits_utmz} (__utmz)

Current session start: {time_session_start} (__utma)
Pageviews in this session: {count_session_pageviews} (__utmb)

Search term used: {value_search_term} (__utmz)
Source of visit: {value_visit_source} (__utmz)

Number of outbound clicks: {count_outbound_clicks} (__utmb)

Client identifier: {value_client_identifier} (_ga)
Visitor identifier: {value_visitor_identifier} (__utma)"""

def format_string_default(string, dictionary, default="<not found>"):
    """
    Format a string with keys in the dictionary, using default value
    default if any {format} key in the string is not found in the dict
    """
    class Default(dict):
        """
        Class inheriting from dict, whose purpose is to provide
        the <not-found> string rather than raising when a key
        is not found
        """
        def __missing__(self, key):
            return default

    # Create our dict with the format placeholder names as keys
    info_dict = Default(dictionary)
    return string.format_map(info_dict)
