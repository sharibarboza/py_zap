import unittest
from datetime import datetime

from bs4 import BeautifulSoup

from pyzap.constants import BASE_URL, DATE_FMT
import pyzap.utils as u
from pyzap.search import SearchDaily
from pyzap import Cable, Broadcast



class TestCableRatings(unittest.TestCase):

    def setUp(self):
        self.date = 'July 25 2017'
        self.ratings = Cable(self.date)

    def test_correct_fields(self):
        """Test Cable ratings object has correct arguments"""
        self.assertEqual(self.date, self.date)
        self.assertTrue(len(self.ratings) > 0)

    def test_valid_entries(self):
        """Test Cable rating entries have valid fields"""
        for entry in self.ratings:
            self.assertTrue(len(entry['show']) > 0)
            self.assertTrue(len(entry['net']) > 0)
            self.assertTrue(len(entry['time']) > 0)
            self.assertTrue(entry['viewers'] > 0)
            self.assertTrue(entry['rating'] > 0)


class TestBroadcastRatings(unittest.TestCase):

    def setUp(self):
        self.date = 'July 25 2017'
        self.ratings = Broadcast(self.date)

    def test_correct_fields(self):
        """Test Broadcast ratings object has correct arguments"""
        self.assertEqual(self.date, self.date)
        self.assertTrue(len(self.ratings) > 0)

    def test_valid_entries(self):
        """Test Broadcast rating entries have valid fields"""
        for entry in self.ratings:
            self.assertTrue(len(entry['show']) > 0)
            self.assertTrue(len(entry['net']) > 0)
            self.assertTrue(len(entry['time']) > 0)
            self.assertTrue(entry['viewers'] > 0)
            self.assertTrue(entry['rating'] > 0)
            self.assertTrue(entry['share'] > 0)

    def test_get_averages(self):
        """Test getting network averages for Broadcast ratings"""
        networks = ['NBC', 'ABC', 'CBS', 'CW', 'FOX']
        averages = self.ratings.get_averages()
        self.assertTrue(isinstance(averages, dict))
        self.assertTrue(len(averages) == 5)

        for network in networks:
            self.assertTrue(network in averages)


class TestInvalidDate(unittest.TestCase):

    def test_page_not_found_error(self):
        """Test assertion of page not found error with invalid date"""
        date = 'July 25 ' + str(datetime.today().year + 1)
        self.assertRaises(u.PageNotFoundError, Broadcast, date)


class TestRatingsLimit(unittest.TestCase):

    def setUp(self):
        self.date = 'July 25 2017'
        self.limit = 6
        self.ratings = Broadcast(self.date, limit=self.limit)

    def test_has_6_ratings(self):
        """Test that the ratings is only limited to 6 results"""
        self.assertEqual(len(self.ratings), self.limit)


class TestUtils(unittest.TestCase):

    def test_convert_string(self):
        """Test that string returns string with specific characters"""
        string = 'July-25/2017'
        clean_string = u.convert_string(string, ['-', '/'])
        self.assertEqual(clean_string, 'July 25 2017')

    def test_convert_time(self):
        """Test that time string is converted to 24-hour time"""
        time = '8:30 PM'
        military_time = u.convert_time(time)
        self.assertEqual(military_time, '20:30 PM')

    def test_convert_month_shorten(self):
        """Test shortening a month name from a date string"""
        short_month = u.convert_month('January 15')
        self.assertEqual(short_month, 'jan 15')

    def test_convert_month_lengthen(self):
        """Test lengthening a month name from a date string"""
        long_month = u.convert_month('Jan 15', shorten=False)
        self.assertEqual(long_month, 'january 15')

    def test_convert_date(self):
        """Test string date converts to a datetime object"""
        date = 'July 16 2017'
        date_obj = u.convert_date(date)
        self.assertTrue(isinstance(date_obj, datetime))

    def test_convert_date_fail(self):
        """Test that wrong date format raises ValueError"""
        date = '2017 July 16'
        self.assertRaises(ValueError, u.convert_date, date)

    def test_get_soup(self):
        """Test url converts to BeautifulSoup objects"""
        url = 'http://tvbythenumbers.zap2it.com/daily-ratings/tv-ratings-tuesday-july-25-2017/'
        soup = u.get_soup(url)
        self.assertTrue(isinstance(soup, BeautifulSoup))

    def test_get_day(self):
        """Test date objects return correct day string"""
        date = 'July 25 2017'
        date_obj = u.convert_date(date)
        day = u.get_day(date_obj)
        self.assertEqual(day, 'Tuesday')

    def test_date_in_range(self):
        """Test two date strings are within specific range span"""
        date1 = 'July 25 2017'
        date2 = 'July 28 2017'
        self.assertTrue(u.date_in_range(date1, date2, 5))

    def test_date_not_in_range(self):
        """Test two date strings are not within specific range span"""
        date1 = 'July 25 2017'
        date2 = 'July 31 2017'
        self.assertFalse(u.date_in_range(date1, date2, 5))

    def test_inc_date(self):
        """Test date is incremented a number of days"""
        date = 'July 25 2017'
        date_obj = u.convert_date(date)
        inc_date = u.inc_date(date_obj, 4, DATE_FMT)
        self.assertEqual(inc_date, 'July 29 2017')

    def test_match_words_success(self):
        """Test if a phrase successfully matches a word list"""
        phrase = 'It\'s Always Sunny in Philadelphia'
        query = 'always sunny philadelphia'
        self.assertTrue(u.match_words(query.split(), phrase))

    def test_match_words_fail(self):
        """Test if a phrase unsuccessfully matches a word list"""
        phrase = 'Survivor'
        query = 'designated survivor'
        self.assertFalse(u.match_words(query.split(), phrase))


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
        self.assertRaises(u.PageNotFoundError, search.fetch_result)



if __name__ == '__main__':
    unittest.main()