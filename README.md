# Tripadvisor Crawler

[![screenshot.png](https://raw.githubusercontent.com/efazati/tripadvisor-crawler/master/screenshot.png)](https://raw.githubusercontent.com/efazati/tripadvisor-crawler/master/screenshot.png)

In this project you should select countries and after that this project will download all resturant and things to do
also you can generate kml from that things for import to google map


## Installation


.. code-block:: sh

	$ git clone https://github.com/efazati/tripadvisor-crawler.git
	$ cd tripadvisor-crawler

now you can create sample file for get detail of your countries

.. code-block:: sh

	$ nano sample.py

after that you can find index id from url of tripadvisor link


.. code-block:: python

	from crawler import get_cities, get_detail_of_city

	def main():
	    countries = [
	        {'index': 'g293998', 'country': 'Iran'},
	        {'index': 'g293860', 'country': 'India'},
	        {'index': 'g294211', 'country': 'China'},
	        {'index': 'g187275', 'country': 'Germany'},
	        {'index': 'g187768', 'country': 'Italy'},
	        {'index': 'g294459', 'country': 'Russia'},
	        {'index': 'g293969', 'country': 'Turkey'},
	        {'index': 'g293951', 'country': 'Malaysia'},
	    ]
	    cities = []
	    for country in countries:
	        cities += get_cities(country)

	    for item in cities:
	        get_detail_of_city(item)
	    return

Note: for better log interface you can install
https://github.com/powerline/fonts
