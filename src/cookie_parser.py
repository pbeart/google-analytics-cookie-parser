"""
Provide helper functions and classes for parsing cookies and GA cookie
info from supported browsers
"""

import sqlite3
from urllib.request import pathname2url
import csv

import parser_helpers

def get_cookie_fetcher(browser, *args, **kwargs):
    """
    Returns the appropriate CookieFetcher subclass for the given
    browser shortname
    """

    if browser == "firefox.3+":
        return Firefox3Fetcher(*args, **kwargs)
    elif browser == "csv":
        return CSVFetcher(*args, **kwargs)

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

class CSVFetcher(CookieFetcher):
    """
    CookieFetcher for fetching from CSV files
    """
    def __init__(self, file_path, cookie_names):
        # pylint: disable=super-init-not-called

        self.cookie_names = cookie_names
        self.error = None

        self.file_path = file_path

        with open(file_path, "r") as self.csv_file:
            try:
                self.csv_dialect = csv.Sniffer().sniff(self.csv_file.read(1024))
            except csv.Error:
                self.error = "Error trying to parse .csv file"
                return


            self.csv_file.seek(0) # Need to reset back to start after sniffing

            reader = csv.reader(self.csv_file, self.csv_dialect)

            # We need to find out which columns correspond to which values, so
            # use find_headers
            self.header_indices = self.find_headers(next(reader))

        # If any of the header names couldn't be found
        if None in self.header_indices.values():
            not_found = ", ".join([k for k, v in self.header_indices.items() if v is None])
            self.error = "Could not find the column headers: {}".format(not_found)
            return

    def find_headers(self, row):
        """
        Return a dict of the column indexes in which the fields name, value,
        host, and create_time are found in the given header row, in the format
        {"name": n1, "value": n2, ...}
        """
        keywords = {"name": ["name"],
                    "value": ["value"],
                    "host": ["host", "site", "domain"],
                    "create_time": ["create_time", "creation time", "create time"]}

        keyword_indices = {"name": None,
                           "value": None,
                           "host": None,
                           "create_time": None}

        # For every column in the header row, try to match it to a header name
        # by checking if it contains any of the relevant keywords, and from
        # this update the keyword_indices dict with the found index

        for column_index, column in enumerate(row):
            # Header names, who have key values of None in keyword_indices,
            # i.e. whose column index has not yet been found.
            filtered_headers = [k for k, v in keyword_indices.items() if v is None]
            for possible_column_name in filtered_headers:
                # The column contains one of the keywords
                if any([i in column.lower() for i in keywords[possible_column_name]]):
                    keyword_indices[possible_column_name] = column_index

        return keyword_indices


    def get_domains(self):
        with open(self.file_path, "r") as self.csv_file:
            reader = csv.reader(self.csv_file, self.csv_dialect)

            # Get rid of the header row from the reader
            next(reader)

            # All rows containing GA cookies
            ga_rows = [row for row in reader\
                       if row[self.header_indices["name"]] in self.cookie_names]

            # Find all domains by getting the nth element of each row, where
            # n is the index of the host value header from header_indices
            all_domains = [row[self.header_indices["host"]] for row in ga_rows]

            # Use set to make list unique
            unique_domains = list(set(all_domains))
        return unique_domains

    def get_domain_info(self, domain):
        with open(self.file_path, "r") as self.csv_file:
            reader = csv.reader(self.csv_file, self.csv_dialect)

            # Get rid of the header row from the reader
            next(reader)

            # Find all rows with GA cookies with this domain
            domain_rows = [row for row in reader\
                           if row[self.header_indices["host"]] == domain\
                            and row[self.header_indices["name"]] in self.cookie_names]

            structured_rows = [[row[self.header_indices["name"]],
                                row[self.header_indices["value"]]] for row in domain_rows]
        return parser_helpers.ga_summary(structured_rows)

    def get_cookie_count(self):
        with open(self.file_path, "r") as self.csv_file:
            reader = csv.reader(self.csv_file, self.csv_dialect)

            # All rows containing GA cookies
            ga_rows = [row for row in reader\
                       if row[self.header_indices["name"]] in self.cookie_names]
            return len(ga_rows)

    def get_cookies(self, cookie_name):
        with open(self.file_path, "r") as self.csv_file:
            reader = csv.reader(self.csv_file, self.csv_dialect)

            # Create a list of lists in the form:
            # [[Cookie host, Creation time, Value], ...]
            structured_rows = [[row[self.header_indices["host"]],
                                row[self.header_indices["create_time"]],
                                row[self.header_indices["value"]]] for row in reader\
                               if row[self.header_indices["name"]] == cookie_name]

        return parser_helpers.ga_generate_table(structured_rows, cookie_name)

class Firefox3Fetcher(CookieFetcher):
    """
    CookieFetcher for Firefox 3+
    """
    def __init__(self, filepath, cookie_names):
        # pylint: disable=super-init-not-called

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
            self.cursor.execute("SELECT name FROM sqlite_master \
WHERE type='table' AND name='moz_cookies';")
            # moz_cookies table not present
            if self.cursor.fetchone() is None:
                self.error = "The selected file was a valid database \
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

        return parser_helpers.ga_summary(self.cursor.fetchall())

    def get_cookies(self, cookie_name):
        # Create a list of lists in the form:
        # [[Cookie host, Creation time, Value], ...]
        self.cursor.execute("SELECT host, creationTime, value FROM moz_cookies WHERE name = ?",
                            [cookie_name])

        rows = []

        # Convert creationTime in all rows from microseconds to seconds
        for row in self.cursor.fetchall():
            row_list = list(row)
            try:
                row_list[1] = float(row[1])/1000000 # Convert from microseconds to seconds
                print("Converted to {}".format(row_list))
            except ValueError:
                raise
                pass # Could not be converted to float
            finally:
                rows.append(tuple(row_list))

        return parser_helpers.ga_generate_table(rows, cookie_name)

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
