#!/usr/bin/env python\

from .constants import BASE_URL, SEARCH_URL, PAGE_ERROR
from .utils import PageNotFoundError, get_day, get_soup, convert_date, date_in_range

class SearchDaily(object):
    """Uses the search page to search for daily ratings pages based on
    specific category and date.
    """

    def __init__(self, category, date):
        """If requesting ratings within the last 2 days (especially on
        weekends) and page is not found, the ratings page has most likely
        not been posted yet.

        :param category: 'cable', broadcast', 'final' or 'tv' (non-final)
        :param date: Must be formatted as Month Date Year (e.g. January 6 2016)
        """
        self._assert_category(category)

        self.category = category
        self.date = date
        self.date_obj = convert_date(date)
        self.month = self.date_obj.month
        self.day = get_day(self.date_obj)
        self.year = self.date_obj.year

        self.url = self._build_url()
        self.soup = get_soup(self.url)
        self.results = []

    def get_url(self):
        """Returns the built url."""
        return self.url

    def get_soup(self):
        """Returns the HTML object"""
        return self.soup

    def fetch_result(self):
        """Return a list of urls for each search result."""
        results = self.soup.find_all('div', {'class': 'container container-small'})
        href = None
        is_match = False

        i = 0
        while i < len(results) and not is_match:
            result = results[i]
            anchor = result.find('a', {'rel': 'bookmark'})
            is_match = self._filter_results(result, anchor)
            href = anchor['href']

            i += 1

        try:
            page = get_soup(href)
        except (Exception):
            page = None

        # Return page if search is successful
        if href and page:
            return page
        else:
            raise PageNotFoundError(PAGE_ERROR)

    def _filter_results(self, result, anchor):
        """Filter search results by checking category titles and dates"""
        valid = True

        try:
            cat_tag = result.find('a', {'rel': 'category tag'}).string
            title = anchor.string.lower()
            date_tag = result.find('time').string
        except (AttributeError, TypeError):
            return False      
             
        if cat_tag != "Daily Ratings":
            valid = False
        if not date_in_range(self.date, date_tag, 5):
            valid = False
        if self.category == 'cable' and 'cable' not in title:
            valid = False
        elif self.category != 'cable' and 'cable' in title:
            valid = False

        return valid

    def _build_url(self):
        """Build url based on searching by date or by show."""
        url_params = [
            BASE_URL, self.category + ' ratings', self.day, self.year, self.month
        ]

        return SEARCH_URL.format(*url_params)

    def _assert_category(self, category):
        """Validate category argument"""
        category = category.lower()
        valid_categories = ['cable', 'broadcast', 'final', 'tv']
        assert_msg = "%s is not a valid category." % (category)
        assert (category in valid_categories), assert_msg
