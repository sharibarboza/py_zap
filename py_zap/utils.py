#!/usr/bin/env python
from __future__ import print_function, absolute_import

import json
import requests
import calendar
import sys
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from .constants import HEADERS, MONTHS, SHORT_MONTHS, DATE_FMT

if sys.version_info[0] == 3:
    PY3 = True
else:
    PY3 = False

if PY3:
    sys.tracebacklimit = None
else:
    sys.tracebacklimit = 0


class PageNotFoundError(Exception):
    """Raise exception when page is not found."""
    pass


def to_json(data):
    """Return data as a JSON string."""
    return json.dumps(data, default=lambda x: x.__dict__, sort_keys=True, indent=4)

def convert_string(string, chars=None):
    """Remove certain characters from a string."""
    if chars is None:
        chars = [',', '.', '-', '/', ':', '  ']

    for ch in chars:
        if ch in string:
            string = string.replace(ch, ' ')
    return string

def convert_float(string):
    """Convert string into a float, otherwise return string."""
    try:
        return float(string)
    except (ValueError, TypeError):
        return string

def convert_time(time):
    """Convert a time string into 24-hour time."""
    split_time = time.split()
    try:
        # Get rid of period in a.m./p.m.
        am_pm = split_time[1].replace('.', '')
        time_str = '{0} {1}'.format(split_time[0], am_pm)
    except IndexError:
        return time
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p')
    except ValueError:
        time_obj = datetime.strptime(time_str, '%I %p')

    return time_obj.strftime('%H:%M %p')

#----------------------------------------------------------
# Date helpers
#----------------------------------------------------------

def convert_month(date, shorten=True, cable=True):
    """Replace month by shortening or lengthening it.

    :param shorten: Set to True to shorten month name.
    :param cable: Set to True if category is Cable.
    """
    month = date.split()[0].lower()
    if 'sept' in month:
        shorten = False if cable else True

    try:
        if shorten:
            month = SHORT_MONTHS[MONTHS.index(month)]
        else:
            month = MONTHS[SHORT_MONTHS.index(month)]
    except ValueError:
        month = month.title()

    return '{0} {1}'.format(month, ' '.join(date.split()[1:]))

def convert_date(date):
    """Convert string to datetime object."""
    date = convert_month(date, shorten=False)
    clean_string = convert_string(date)
    return datetime.strptime(clean_string, DATE_FMT.replace('-',''))

def get_day(date_obj):
    """Get the name of the day based on the date object."""
    return calendar.day_name[date_obj.weekday()]

def date_in_range(date1, date2, range):
    """Check if two date objects are within a specific range"""
    date_obj1 = convert_date(date1)
    date_obj2 = convert_date(date2)
    return (date_obj2 - date_obj1).days <= range

def inc_date(date_obj, num, date_fmt):
    """Increment the date by a certain number and return date object.
    as the specific string format.
    """
    return (date_obj + timedelta(days=num)).strftime(date_fmt)

def next_week(date_obj):
    """Return 7 days after the date object."""
    return inc_date(date_obj, 7, DATE_FMT)


def last_week(date_obj):
    """Return 7 days before the date object."""
    return inc_date(date_obj, -7, DATE_FMT)


#----------------------------------------------------------
# Parsing helpers
#----------------------------------------------------------

def get_soup(url):
    """Request the page and return the soup."""
    html = requests.get(url, stream=True, headers=HEADERS)
    if html.status_code != 404:
        return BeautifulSoup(html.content, 'html.parser')
    else:
        return None

def match_list(query_list, string):
    """Return True if all words in a word list are in the string.

    :param query_list: list of words to match
    :param string: the word or words to be matched against
    """
    # Get rid of 'the' word to ease string matching
    match = False
    index = 0
    string = ' '.join(filter_stopwords(string))

    if not isinstance(query_list, list):
        query_list = [query_list]

    while index < len(query_list):
        query = query_list[index]
        words_query = filter_stopwords(query)
        match = all(word in string for word in words_query)
        if match:
            break

        index += 1

    return match    

def filter_stopwords(phrase):
    """Filter out stop words and return as a list of words"""
    if not isinstance(phrase, list):
        phrase = phrase.split()

    stopwords = ['the', 'a', 'in', 'to']
    return [word.lower() for word in phrase if word.lower() not in stopwords]


def unescape_html(string):
    """Replace non-breaking space with white space."""
    return safe_unicode(string).replace('\xa0', ' ')


def safe_unicode(string):
    """If Python 2, replace non-ascii characters and return encoded string."""
    if not PY3:
        uni = string.replace(u'\u2019', "'")
        return uni.encode('utf-8')
        
    return string

def get_strings(soup, tag):
    """Get all the string children from an html tag."""
    tags = soup.find_all(tag)
    strings = [s.string for s in tags if s.string]
    return strings

def exceeded_limit(limit, length):
    """Check if the length exceeds a limit"""
    return True if limit and length >= limit else False
