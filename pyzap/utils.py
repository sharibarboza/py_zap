#!/usr/bin/env python
from __future__ import print_function, absolute_import

import json
import requests
import calendar
import sys
from datetime import timedelta

from bs4 import BeautifulSoup

from .constants import HEADERS, DATE_FMT

from datetime import datetime

from .constants import MONTHS, SHORT_MONTHS, DATE_FMT


class PageNotFoundError(Exception):
    """Raise exception when page is not found."""
    pass


def get_soup(url):
    """Request the page and return the soup."""
    html = requests.get(url, stream=True, headers=HEADERS)
    if html.status_code != 404:
        return BeautifulSoup(html.content, 'html.parser')
    else:
        return None

def convert_string(s):
    """Remove certain characters from date string."""
    chars = [',', '.', '-', '/', ':', '  ']
    for ch in chars:
        if ch in s:
            s = s.replace(ch, ' ')
    return s

def convert_month(date, shorten=True, cable=True):
    """Replace month by shortening or lengthening it.

    :param shorten: Set to True to shorten month name."""
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
    return datetime.strptime(convert_string(date), DATE_FMT.replace('-',''))

def get_day(date_obj):
    """Get the name of the day based on the date object."""
    return calendar.day_name[date_obj.weekday()]

def date_in_range(date1, date2, range):
	"""Check if two date objects are within a specific range"""
	date_obj1 = convert_date(date1)
	date_obj2 = convert_date(date2)
	return (date_obj2 - date_obj1).days <= range