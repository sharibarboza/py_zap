import unittest
from datetime import datetime

from bs4 import BeautifulSoup

from pyzap.constants import BASE_URL
from pyzap.utils import PageNotFoundError, get_soup, convert_date, get_day, date_in_range
from pyzap.search import SearchDaily


class TestConvert(unittest.TestCase):

    def test_convert_date(self):
        """Test string date converts to a datetime object"""
        date = 'July 16 2017'
        date_obj = convert_date(date)
        self.assertTrue(isinstance(date_obj, datetime))

    def test_convert_date_fail(self):
        """Test that wrong date format raises ValueError"""
        date = '2017 July 16'
        self.assertRaises(ValueError, convert_date, date)


class TestUtils(unittest.TestCase):

    def test_get_soup(self):
        """Test url converts to BeautifulSoup objects"""
        url = 'http://tvbythenumbers.zap2it.com/daily-ratings/tv-ratings-tuesday-july-25-2017/'
        soup = get_soup(url)
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_day(self):
        """Test date objects return correct day string"""
        date = 'July 25 2017'
        date_obj = convert_date(date)
        day = get_day(date_obj)
        self.assertEqual(day, 'Tuesday')

    def test_date_in_range(self):
        """Test two date strings are within specific range span"""
        date1 = 'July 25 2017'
        date2 = 'July 28 2017'
        self.assertTrue(date_in_range(date1, date2, 5))

    def test_date_not_in_range(self):
        """Test two date strings are not within specific range span"""
        date1 = 'July 25 2017'
        date2 = 'July 31 2017'
        self.assertFalse(date_in_range(date1, date2, 5))


class TestSearchDaily(unittest.TestCase):

    def test_build_url(self):
        """Test SearchDaily returns correct search url"""
        category = 'Broadcast'
        date = 'July 25 2017'
        search = SearchDaily(category, date)
        url = search.get_url()
        expected_url = '/?s=Broadcast ratings+Tuesday&year=2017&monthnum=7&day&category=daily-ratings'
        self.assertEqual(url, BASE_URL + expected_url)

    def test_category_assertion(self):
        """Test invalid category raises assertion"""
        category = 'None'
        date = 'July 25 2017'
        self.assertRaises(AssertionError, SearchDaily, category, date)

    def test_result_found(self):
        """Test if successful result is found"""
        category = 'Broadcast'
        date = 'July 25 2017'
        search = SearchDaily(category, date)
        result = search.fetch_result()
        self.assertTrue(isinstance(result, BeautifulSoup))

    def test_result_not_found(self):
        """Test unsuccessful result returns PageNotFoundError"""
        category = 'Broadcast'
        year = datetime.today().year + 1
        date = 'July 25 ' + str(year)
        search = SearchDaily(category, date)
        self.assertRaises(PageNotFoundError, search.fetch_result)



if __name__ == '__main__':
    unittest.main()