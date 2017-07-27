from .utils import convert_float, convert_time, convert_date
from .constants import FLOAT_ATTRIBUTES, NONFLOAT_ATTRIBUTES

class InvalidSortError(Exception):
    """Raise exception when sort parameter is not valid."""

    def __init__(self, sort):
        self.sort = sort

    def __str__(self):
        e = ('\'{0}\' is not a valid sort parameter.\n'
             'Valid parameters: {1}')
        return e.format(self.sort, str(FLOAT_ATTRIBUTES + NONFLOAT_ATTRIBUTES))


class Sorter(object):
    """Sort ratings objects by a specific attribute."""

    def __init__(self, rating, category, sort):
        """Sorting a ratings or show object will change the order of its entries.

        :param rating: A ratings object (cable or broadcast) or show object.
        :param category: cable or broadcast.
        :param sort: show, net, time, viewers, rating, or share (broadcast only)
        """
        if sort == 'share':
            assert category != 'cable', '"share" parameter for broadcast ratings only.'

        self.data = rating
        self.sort = sort

    def get_reverse(self):
        """By default, Cable entries are sorted by rating and Broadcast ratings are
        sorted by time.
        By default, float attributes are sorted from highest to lowest and non-float
        attributes are sorted alphabetically (show, net) or chronologically (time).
        """
        if self.sort in FLOAT_ATTRIBUTES:
            return True
        elif self.sort in NONFLOAT_ATTRIBUTES:
            return False
        else:
            raise InvalidSortError(self.sort)

    def sort_func(self, entry):
        """Return the key attribute to determine how data is sorted.
        Time will need to be converted to 24 hour time.
        In instances when float attributes will have an 'n/a' string, return 0.
        """
        key = entry[self.sort]

        if self.sort in FLOAT_ATTRIBUTES and not isinstance(key, float):
            return 0  # If value is 'n/a' string
        elif self.sort == 'time':
            return convert_time(key)
        elif self.sort == 'date':
            return convert_date(key)

        return key

    def sort_entries(self):
        """Get whether reverse is True or False. Return the sorted data."""
        return sorted(self.data, key=self.sort_func, reverse=self.get_reverse())
