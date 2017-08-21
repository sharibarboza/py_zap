from datetime import datetime, timedelta

DATE_FMT = '%B %-d %Y'
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime(DATE_FMT)

HEADERS = {'User-Agent': 'zap2it.py (https://github.com/sharibarboza/zap2it)'}

BASE_URL = 'http://tvbythenumbers.zap2it.com'
URL_FORMAT = '{0}/daily-ratings/{1}-{2}-{3}/'
SEARCH_URL = '{0}/?s={1}+{2}&year={3}&monthnum={4}&day&category=daily-ratings'

MONTHS = [
    'january', 'february', 'march', 'april',
    'may', 'june', 'july', 'august',
    'september', 'october', 'november', 'december'
]
SHORT_MONTHS = [
    'jan', 'feb', 'march', 'april',
    'may', 'june', 'july', 'aug',
    'sept', 'oct', 'nov', 'dec'
]

FLOAT_ATTRIBUTES = ['viewers', 'rating', 'share']
NONFLOAT_ATTRIBUTES = ['show', 'net', 'time', 'date']

PAGE_ERROR = "The page cannot be found."
