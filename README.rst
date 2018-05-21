py_zap
======

py_zap is a Python scraper for fetching daily broadcast and cable ratings from tvbythenumbers.zap2it.com.

Installation
------------

To install with pip:

>>> pip install py_zap

Or clone this repository and run:

>>> python setup.py install

**Broadcast Ratings**

Let's fetch the `final broadcast ratings for October 27, 2016.`_

.. _final broadcast ratings for October 27, 2016.: http://tvbythenumbers.zap2it.com/daily-ratings/thursday-final-ratings-oct-27-2016/

* **If no date parameter is included, it will default to yesterday's date**

>>> from py_zap import Broadcast
>>> ratings = Broadcast('October 27, 2016')

* Now we can look at the chart entries:

>>> entry = ratings[0]     # Gives the 1st entry
>>> entry.show             # Get the name of the show
'The Big Bang Theory'
>>> entry.viewers          # Get the number of viewers (in millions)
14.3
>>> entry.rating           # Get the rating (percentage)
3.4

* We can also ``print`` out the whole chart by:

>>> print(ratings)


>>>
Final Broadcast Ratings for Thursday, October 27 2016
|Show                          |Time      |Network|Viewers|Rating |Share  |
+-------------------------------------------------------------------------+
|The Big Bang Theory           |    8 p.m.|    CBS|   14.3|    3.4|   13.0|
|Grey’s Anatomy                |    8 p.m.|    ABC|    8.2|    2.2|    8.0|
|Superstore                    |    8 p.m.|    NBC|    4.2|    1.3|    5.0|
|Rosewood                      |    8 p.m.|    FOX|    3.4|    0.8|    3.0|
|Legends of Tomorrow           |    8 p.m.| The CW|    1.8|    0.6|    2.0|
|The Great Indoors             | 8:30 p.m.|    CBS|    8.8|    1.9|    7.0|
|The Good Place                | 8:30 p.m.|    NBC|    3.9|    1.2|    4.0|
|Mom                           |    9 p.m.|    CBS|    7.0|    1.5|    5.0|
|Chicago Med                   |    9 p.m.|    NBC|    7.1|    1.5|    5.0|
|Notorious                     |    9 p.m.|    ABC|    3.8|    0.8|    3.0|
|Pitch                         |    9 p.m.|    FOX|    2.9|    0.8|    3.0|
|Supernatural                  |    9 p.m.| The CW|    1.7|    0.6|    2.0|
|Life in Pieces                | 9:30 p.m.|    CBS|    6.0|    1.4|    5.0|
|Pure Genius                   |   10 p.m.|    CBS|    6.2|    1.0|    4.0|
|The Blacklist                 |   10 p.m.|    NBC|    5.5|    1.2|    4.0|
|How to Get Away with Murder   |   10 p.m.|    ABC|    4.1|    1.2|    4.0|

By default, the final broadcast ratings are fetched. To access the fast ratings, which are posted earlier but less accurate, set 'final' param to False. If there are no final ratings available, it will redirect to fast access ratings.

>>> ratings = Broadcast('October 27, 2016', final=False)

**Cable Ratings**

To fetch the `cable ratings for October 27, 2016:`_

.. _cable ratings for October 27, 2016\:: http://tvbythenumbers.zap2it.com/daily-ratings/thursday-cable-ratings-october-27-2016/

>>> from py_zap import Cable
>>> ratings = Cable('October 27, 2016')

Other things you can do
-----------------------

**Sort chart results**

* Broadcast or cable ratings can be sorted based on *show*, *net*, *time*, *rating*, or *viewers*
* Broadcast ratings only can be sorted on *share*

>>> ratings = Cable('October 27, 2016').sort('viewers')    # Sort cable ratings by viewers

>>> ratings = Broadcast('October 27, 2016').sort('share')  # Sort broadcast ratings by share (broadcast only)

**Fetch specific shows or networks**

* Pass a list if you want to fetch more than one

>>> ratings = Broadcast('October 27, 2016', show='Supernatural')     # Fetch a specific show

>>> ratings = Broadcast('October 27, 2016', network=['CBS', 'NBC'])  # Fetch a specific network

**Iterate through multiple weeks**
>>> next_week = ratings.get_next_week()  # Get next week's date

>>> last_week = ratings.get_last_week()  # Get last week's date

**Get network averages (broadcast only)**

>>> averages = ratings.get_averages()  # Get the ratings/viewers averages for broadcast networks
>>> averages['NBC']
{'rating': 1.3, 'viewers': 5.56, 'share': 5.0}

Dependencies
------------

* `Beautiful Soup 4`_

.. _Beautiful Soup 4: https://www.crummy.com/software/BeautifulSoup/

* `requests`_

.. _requests: http://requests.readthedocs.io/en/latest/

License
-------

* This project is under the MIT License.
* All content is owned by Tribune Media Company. See zap2it.com's `Terms of Service`_ for more details.

.. _Terms of Service: http://screenertv.com/terms-of-service/

