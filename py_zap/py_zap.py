#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Python scraper for fetching Broadcast and Cable TV ratings from 
tvbythenumbers.zap2it.com

MIT License

Copyright (c) 2017 Sharidan Barboza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import re

from .utils import *
from .constants import YESTERDAY, URL_FORMAT, BASE_URL, SEARCH_URL, PAGE_ERROR
from .search import SearchDaily
from .sorter import Sorter


class Entry(object):
    """A single row/entry in a cable or broadcast ratings chart."""

    def __init__(self, **kwargs):
        """Contains attributes for a row in a daily ratings chart.

        :param show: The name of the TV show.
        :param net: The name of the network.
        :param time: The time the show airs.
        :param rating: The percentage of all TV-households viewing show.
        :param viewers: The number of viewers in millions.
        :param share: For Broadcast only. The percentage of TV's currently on
                      that are viewing the show.
        """
        for key, value in kwargs.items():
            kwargs[key] = convert_float(safe_unicode(value))
        self.__dict__.update(kwargs)

    def __repr__(self):        
        """Format row for entry object in a ratings chart"""
        s = None

        try: 
            # Set width for network column (cable has longer width)
            width = 7 if hasattr(self, 'share') else 16

            s = '|{:<30.30s}|{:>10s}|'.format(self.show, self.time)
            s += '{0:>{1}.{2}}|'.format(self.net, width, width)
            s += '{:7.2f}|{:7.1f}|'.format(self.viewers, self.rating)

            # For broadcast only
            if hasattr(self, 'share'):
                s += '{:7.1f}|'.format(self.share)
        except TypeError:
            # Return None if entry cannot be represented
            s = None
        finally:
            # Return repr string
            return s

    def __getitem__(self, item):
        """Return entry object when accessed by index"""
        return self.__dict__[item]

    def get_json(self):
        """Represent entry object as a JSON string"""
        return to_json(self)


class Ratings(object):
    """Finds and parses charts from a ratings page."""

    def __init__(self, **kwargs):
        """Main parent class for fetching entries from a ratings chart.

        :param category: cable, final, or tv (non-final broadcast)
        :param show: Will only fetch data of a specific show.
        :param network: Will only fetch data of a specific network.
        :param limit: Will stop fetching data once the limit has been reached.
        :param date: Default - yesterday's date.
        """

        # Convert show and network attributes to lists
        for attr in ["show", "network"]:
            key = kwargs.get(attr)
            if key is not None and not isinstance(key, list):
                kwargs[attr] = [key]                            
        self.__dict__.update(kwargs)

        self.date_obj = convert_date(self.date)
        self.weekday = get_day(self.date_obj)
        self.soup = self._get_ratings_page()
        self.next_week = next_week(self.date_obj)
        self.last_week = last_week(self.date_obj)

        # After finding the page, grab the results
        if self._verify_page():
            self.entries = self.fetch_entries()
        else:
            raise PageNotFoundError(PAGE_ERROR)

    def sort(self, attr):
        """Sort the ratings based on an attribute"""
        self.entries = Sorter(self.entries, self.category, attr).sort_entries()
        return self

    def get_all(self, attr):
        """Returns a list of the requested attribute from all entries"""
        return [entry[attr] for entry in self.entries]

    def get_url(self):
        """Get the ratings page url"""
        return self.url

    def get_date(self):
        """Get the ratings page date"""
        return self.date

    def get_next_week(self):
        """Get the date object for next week"""
        return self.next_week

    def get_last_week(self):
        """Get the date object for last week"""
        return self.last_week

    def get_title(self):
        """Title is either the chart header for a cable ratings page or above
        the opening description for a broadcast ratings page.
        """
        if self.category == 'cable':
            strings = get_strings(self.soup, 'strong')
        else:
            strings = get_strings(self.soup, 'b')

        if len(strings) >= 1 and self.category == 'cable':
            return strings[0]
        elif len(strings) > 0 and 'Fast' in strings[-1]:
            return strings[0]

        return ''.join(strings)

    def get_json(self):
        """Serialize ratings object as JSON-formatted string"""
        ratings_dict = {
            'category': self.category,
            'date': self.date,
            'day': self.weekday,
            'next week': self.next_week,
            'last week': self.last_week,
            'entries': self.entries,
            'url': self.url
        }
        return to_json(ratings_dict)

    def get_rows(self):
        raise NotImplementedError('Must be overwritten by subclass.')

    def _build_url(self, shorten=True):
        raise NotImplementedError('Must be overwritten by subclass.')

    def fetch_entries(self):
        raise NotImplementedError('Must be overwritten in subclass.')

    def __iter__(self):
        for entry in self.entries:
            yield entry

    def __getitem__(self, item):
        return self.entries[item]

    def __len__(self):
        return len(self.entries)

    def _get_url_params(self, shorten=True):
        """Returns a list of each parameter to be used for the url format."""
        cable = True if self.category == 'cable' else False
        url_date = convert_month(self.date, shorten=shorten, cable=cable)

        return [
            BASE_URL,
            self.weekday.lower(),
            self.category + '-ratings',
            url_date.replace(' ', '-')
        ]

    def _match_query(self, show, net):
        return self._match_show(show) and self._match_net(net)

    def _match_show(self, show):
        """Match a query for a specific show/list of shows"""
        if self.show:
            return match_list(self.show, show)
        else:
            return True

    def _match_net(self, net):
        """Match a query for a specific network/list of networks"""
        if self.network:
            return match_list(self.network, net)
        else:
            return True

    def _verify_page(self):
        """Verify the ratings page matches the correct date"""
        title_date = self._get_date_in_title().lower()
        split_date = self.date.lower().split()
        split_date[0] = split_date[0][:3]
        return all(term in title_date for term in split_date)

    def _get_date_in_title(self):
        """Extract the date string from the title."""
        title = unescape_html(''.join(self.get_title()))

        # Extract string from header by getting last 3 words
        #date_string = ' '.join(self.get_title().split()[-3:])
        #return convert_string(date_string)
        return convert_string(title)

    def _get_ratings_page(self):
        """Do a limited search for the correct url."""
        # Use current posted date to build url
        self._build_url()
        soup = get_soup(self.url)
        if soup:
            return soup
        
        # Try building url again with unshortened month
        self._build_url(shorten=False)
        soup = get_soup(self.url)
        if soup:
            return soup

        # If not page is found, use search
        return SearchDaily(self.category, date=self.date).fetch_result()


class Cable(Ratings):
    """Ratings subclass that parses daily cable ratings charts."""

    def __init__(self, date=YESTERDAY, show=None, network=None, limit=None):
        """
        Cable shows are shows not belonging to a major broadcast network.
        By default, will output the top 100 cable shows for that day.
        """
        cable_dict = {
            'category': 'cable',
            'date': date,
            'show': show,
            'network': network,
            'limit': limit
        }

        try:
            Ratings.__init__(self, **cable_dict)
        except Exception:
            raise PageNotFoundError(PAGE_ERROR) from None

    def __repr__(self):
        s = 'Cable Ratings for {day}, {date}'.format(
            day=self.weekday, date=self.date.title())
        s += '\n|{:<30s}|{:<10s}|{:<16s}|{:<7s}|{:<7s}|'.format(
            'Show', 'Time', 'Network', 'Viewers', 'Rating')
        s += '\n+' + '-' * 74 + '+'

        for entry in self:
            try:
                s += '\n{0}'.format(entry)
            except TypeError:
                pass
        return s

    def _build_url(self, shorten=True):
        """Build the url for a cable ratings page"""
        self.url = URL_FORMAT.format(*self._get_url_params(shorten=shorten))

    def get_rows(self):
        """Get the rows from a cable ratings chart"""
        return self.soup.find_all('tr')[1:]

    def fetch_entries(self):
        """Fetch data and parse it to build a list of cable entries."""
        data = []
        for row in self.get_rows():
            # Stop fetching data if limit has been met
            if exceeded_limit(self.limit, len(data)):
                break

            entry = row.find_all('td') 
            entry_dict = {}

            show = entry[0].string
            net = entry[1].string
            if not self._match_query(show, net):
                continue

            entry_dict['show'] = show
            entry_dict['net'] = net
            entry_dict['time'] = entry[2].string

            if ',' in entry[3].string:
                entry_dict['viewers'] = entry[3].string.replace(',', '.')
            else:
                entry_dict['viewers'] = '0.' + entry[3].string
            entry_dict['rating'] = entry[4].string

            # Add data to create cable entry
            data.append(Entry(**entry_dict))

        return data


class Broadcast(Ratings):
    """Ratings subclass that parses daily broadcast ratings charts."""

    def __init__(self, date=YESTERDAY, show=None, network=None, limit=None, final=True):
        """
        Broadcast shows are shows belonging to the 5 major US broadcast
        networks: ABC, NBC, CBS, FOX, and the CW.

        Broadcast ratings can be split into two categories: final and
        non-final ("Fast-Affiliate"). Non-final ratings are posted earlier
        than final ratings.

        :param final: Fetch final or 'fast-affiliate' ratings.
        """
        broadcast_dict = {
            'category': 'final' if final else 'tv',
            'date': date,
            'show': show,
            'network': network,
            'limit': limit
        }

        try:
            Ratings.__init__(self, **broadcast_dict)
        except Exception:
            raise PageNotFoundError(PAGE_ERROR) from None

    def __repr__(self):
        if self.category == 'final':
            title_cat = 'Final Broadcast Ratings'
        else:
            title_cat = 'Fast Affiliate Broadcast Ratings'

        s = '{0} for {1}, {2}'.format(
            title_cat, self.weekday, self.date.title())
        s += '\n|{:<30s}|{:10s}|{:7s}|{:7s}|{:7s}|{:7s}|'.format(
            'Show', 'Time', 'Network', 'Viewers', 'Rating', 'Share')
        s += '\n+' + '-' * 73 + '+'

        for entry in self:
            try:
                s += '\n{0}'.format(entry)
            except TypeError:
                pass
        return s

    def _build_url(self, shorten=True):
        """Build the url for a broadcast ratings page"""
        url_order = self._get_url_params(shorten=shorten)

        # For fast ratings, switch weekday and category in url
        if self.category != 'final':
            url_order[1], url_order[2] = url_order[2], url_order[1]
        self.url = URL_FORMAT.format(*url_order)

    def get_rows(self):
        """Get the rows from a broadcast ratings chart"""
        table = self.soup.find_all('tr')[1:-3]
        return [row for row in table if row.contents[3].string]

    def fetch_entries(self):
        """Fetch data and parse it to build a list of broadcast entries."""
        current_time = ''

        data = []
        for row in self.get_rows():
            # Stop fetching data if limit has been met
            if exceeded_limit(self.limit, len(data)):
                break

            entry = row.find_all('td')
            entry_dict = {}

            show_time = entry[0].string
            if show_time and show_time != current_time:
                current_time = show_time
            if not show_time:
                show_time = current_time
            entry_dict['time'] = show_time

            show_string = entry[1].string.split('(')
            show = show_string[0][:-1]
            net = self._get_net(show_string)
            if not self._match_query(show, net):
                continue

            entry_dict['show'] = show
            entry_dict['net'] = net
            entry_dict['viewers'] = entry[3].string.strip('*')
            entry_dict['rating'], entry_dict['share'] = self._get_rating(entry)

            # Add data to initialize broadcast entry
            data.append(Entry(**entry_dict))

        return data

    def get_averages(self):
        """Get the broadcast network averages for that day.

        Returns a dictionary:
        key: network name
        value: sub-dictionary with 'viewers', 'rating', and 'share' as keys
        """
        networks = [unescape_html(n.string) for n in self.soup.find_all('td', width='77')]
        table = self.soup.find_all('td', style=re.compile('^font'))

        # Each element is a list split as [rating, share]
        rateshares = [r.string.split('/') for r in table[:5] if r.string]
        viewers = [v.string for v in table[5:] if v.string]
        averages = {}

        # Load the averages dict
        for index, network in enumerate(networks):
            viewer = convert_float(unescape_html(viewers[index]))
            rating = convert_float(unescape_html(rateshares[index][0]))
            share = convert_float(unescape_html(rateshares[index][1]))
            averages[network] = {'viewer': viewer, 'rating': rating, 'share': share}

        return averages

    def _get_net(self, entry):
        """Get the network for a specific row"""
        try:
            net = entry[1]
            return net[net.find('(')+1:net.find(')')]
        except IndexError:
            return None

    def _get_rating(self, entry):
        """Get the rating and share for a specific row"""
        r_info = ''
        for string in entry[2].strings:
            r_info += string
        rating, share = r_info.split('/')
        return (rating, share.strip('*'))


