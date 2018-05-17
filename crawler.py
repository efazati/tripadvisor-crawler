from datetime import datetime
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re

# from crawler.crawler import Crawled
base_url = 'https://www.tripadvisor.com'
top_activity_url = base_url + '/Attractions-%s-%sActivities-%s.html'
top_restaurants_url = base_url + '/Restaurants-%s-%sActivities-%s.html'

def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    html = requests.get(url, headers=headers)
    print 'Get =>', url
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup

def get_text(item):
    if item:
        return item.get_text()
    return ''


def get_poi(url, data_dict, crawler_list, kind):
    page = get_page(url)

    popularity = get_text(page.find('span', class_='header_popularity'))

    location = page.find(string=re.compile(r"lat:(.*?)"))
    images_obj = page.find('div', class_='page_images').find_all('img', class_='centeredImg noscript')
    images = []
    for image in images_obj:
        images.append(image.get('src'))
    lat_pattern = re.compile(r"lat: (.*?),", re.MULTILINE | re.DOTALL)
    long_pattern = re.compile(r"lng: (.*?),", re.MULTILINE | re.DOTALL)
    lat = lat_pattern.search(location).group(1)
    lng = long_pattern.search(location).group(1)

    description = get_text(page.find('div', class_='description overflow'))
    hours = get_text(page.find('div', class_='section hours'))
    address = get_text(page.find('div', class_='section location'))
    phone = get_text(page.find('div', class_='detail_section phone'))

    if kind == 'resturant':
        data_dict['name'] = get_text(page.find('h1', class_='heading_title'))
    data_dict['comment'] = get_text(page.find('div', class_='prw_reviews_text_summary_hsx'))
    data_dict['popularity'] = popularity
    data_dict['location'] = {'lat': float(lat), 'long': float(lng)}
    data_dict['images'] = images
    data_dict['url'] = url
    data_dict['description'] = description
    data_dict['hours'] = hours
    data_dict['address'] = address
    data_dict['phone'] = phone
    data_dict['type'] = kind
    data_dict['country'] = crawler_list['country']
    data_dict['state'] = crawler_list['state']
    return data_dict

def get_poi_list(db, url, crawler_list, kind):
    pois = []
    page = get_page(url)
    if kind == 'things-to-do':
        items = page.find_all('div', class_='attraction_clarity_cell')
    else:
        items = page.find_all('div', id=lambda x: x and x.startswith('eatery_'))

    for item in items:
        poi = {'href': item.find('a').get('href'),
            'name': item.find('a').get_text().strip()}
        url = base_url + poi['href']
        if is_exists(db, url):
            continue
        poi_data = ''
        try:
            poi_data = get_poi(url, poi, crawler_list, kind)
        except Exception as e:
            print('Error to get', e)
        if poi_data:
            create_or_update_data_mongo(db, poi_data)
    return pois

def crawl_things_to_do_city(db, keys):
    items = []
    for x in xrange(0,6):
        
        url = top_activity_url % (keys['index'], page, keys['name'])
        items += get_poi_list(db, url, keys, 'things-to-do')
    return items

def crawl_resturant_city(db, keys):
    items = []
    for x in xrange(0,1):
        if x == 0:
            page = ''       
        else:
            page = 'oa%s-' % (x*30) 
        
        if 'state' in keys:
            state = keys['state']
        else:
            state = keys['country']
        
        print 'Country => ', keys['country'], state
        if 'name' in keys:
            name = keys['name']
        else:
            name = keys['country']

        url = top_restaurants_url % (keys['index'], page, keys['name'])
        items += get_poi_list(db, url, keys, 'resturant')
    return items

def get_detail_of_city(db, keys):
    crawl_resturant_city(db, keys)
    crawl_things_to_do_city(db, keys)


def get_cities(keys):
    url = top_activity_url % (keys['index'], '', keys['country'])

    page = get_page(url)
    elements = page.find_all('div', class_='ap_navigator')
    items = []
    for element in elements:
        url_bones = element.find('a').get('href').split('-')
        print url_bones
        items.append({'index': url_bones[1], 'name': url_bones[3], 'state': get_text(element).replace('Things to do in ', ''), 'country': country})

    return items 

def get_db():
    client = MongoClient()
    db = client['world']
    return db

def insert_data(db, new_data):
    new_data['create_date'] = datetime.now()
    new_data['updated'] = False
    db.location.insert(new_data)
    return new_data['_id']

def is_exists(db, url):
    if db.location.find_one({'url': url}):
        return True
    return False

def create_or_update_data_mongo(db, new_data):
    if not is_exists(db, new_data['url']):
        return insert_data(db, new_data)
    print('exists')
    return False

def main():
    db = get_db()
    countries = [
            {'index': 'g294000', 'country': 'Iraq'},
            {'index': 'g293860', 'country': 'India'},
            {'index': 'g294459', 'country': 'Russia'},
            {'index': 'g293969', 'country': 'Turkey'},
            {'index': 'g293951', 'country': 'Malaysia'},
            ]
    cities = []
    for country in countries:
        cities += get_cities(country)

    for item in cities:
        get_detail_of_city(db, keys)

    return

if __name__ == "__main__":
    main()
