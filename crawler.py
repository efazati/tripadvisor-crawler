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
        if x == 0:
            page = ''       
        else:
            page = 'oa%s-' % (x*30) 
        print 'Country => ', keys['country'], keys['state']
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
        print 'Country => ', keys['country'], keys['state']
        url = top_restaurants_url % (keys['index'], page, keys['name'])
        items += get_poi_list(db, url, keys, 'resturant')
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
    cities = [
            {'index': 'g298484', 'name': 'Moscow_Central_Russia', 'country': 'Russia', 'state': 'Moscow'},
            {'index': 'g298507', 'name': 'St_Petersburg_Northwestern_District', 'country': 'Russia', 'state': 'Saint Petersburg'},
            {'index': 'g294459', 'name': 'Russia', 'country': 'Russia', 'state': 'Russia'},
            {'index': 'g294195', 'name': 'Tbilisi', 'country': 'Georgia', 'state': 'Tbilisi'},
            {'index': 'g319823', 'name': 'Armenia_Quindio_Department', 'country': 'Armenia', 'state': 'Armenia'},
            {'index': 'g293969', 'name': 'Turkey', 'country': 'Turkey', 'state': 'Turkey'},
            {'index': 'g293951', 'name': 'Malaysia', 'country': 'Malaysia', 'state': 'Malaysia'},
            {'index': 'g297576', 'name': 'Batumi_Adjara_Region', 'country': 'Georgia', 'state': 'Batumi'},
            {'index': 'g298570', 'name': 'Kuala_Lumpur_Wilayah_Persekutuan', 'country': 'Malaysia', 'state': 'Kuala Lumpur'},
            {'index': 'g660694', 'name': 'Penang_Island_Penang', 'country': 'Malaysia', 'state': 'Penang Island'},
            {'index': 'g298303', 'name': 'George_Town_Penang_Island_Penang', 'country': 'Malaysia', 'state': 'George Town'},
            {'index': 'g298283', 'name': 'Langkawi_Langkawi_District_Kedah', 'country': 'Malaysia', 'state': 'Langkawi Langkawi'},
            {'index': 'g298307', 'name': 'Kota_Kinabalu_Kota_Kinabalu_District_West_Coast_Division_Sabah', 'country': 'Malaysia', 'state': 'Kota Kinabalu'},
            {'index': 'g306997', 'name': 'Melaka_Central_Melaka_District_Melaka_State', 'country': 'Malaysia', 'state': 'Melaka Central'},
            {'index': 'g293932', 'name': 'Yerevan', 'country': 'Armenia', 'state': 'Yerevan'},
            {'index': 'g815353', 'name': 'Gyumri_Shirak_Province', 'country': 'Armenia', 'state': 'Gyumri Shirak'},
            {'index': 'g2151208', 'name': 'Tsakhkadzor_Kotayk_Province', 'country': 'Armenia', 'state': 'Tsakhkadzor'},
            {'index': 'g293974', 'name': 'Istanbul', 'country': 'Armenia', 'state': 'Istanbul'},
            {'index': 'g298656', 'name': 'Ankara', 'country': 'Turkey', 'state': 'Ankara'},
            {'index': 'g297962', 'name': 'Antalya_Turkish_Mediterranean_Coast', 'country': 'Turkey', 'state': 'Antalya'},
            {'index': 'g298006', 'name': 'Izmir_Izmir_Province_Turkish_Aegean_Coast', 'country': 'Turkey', 'state': 'Izmir'},
            {'index': 'g297972', 'name': 'Kusadasi_Turkish_Aegean_Coast', 'country': 'Turkey', 'state': 'Kusadasi'},
            {'index': 'g298033', 'name': 'Marmaris_Mugla_Province_Turkish_Aegean_Coast', 'country': 'Turkey', 'state': 'Marmaris Mugla'},
            {'index': 'g298031', 'name': 'Fethiye_Mugla_Province_Turkish_Aegean_Coast', 'country': 'Turkey', 'state': 'Fethiye Mugla'},
            {'index': 'g298520', 'name': 'Kazan_Republic_of_Tatarstan_Volga_District', 'country': 'Russia', 'state': 'Kazan'},
            {'index': 'g298540', 'name': 'Yekaterinburg_Sverdlovsk_Oblast_Urals_District', 'country': 'Russia', 'state': 'Yekaterinburg'},
            {'index': 'g298536', 'name': 'Sochi_Greater_Sochi_Krasnodar_Krai_Southern_District', 'country': 'Russia', 'state': 'Sochi'},
            {'index': 'g298515', 'name': 'Nizhny_Novgorod_Nizhny_Novgorod_Oblast_Volga_District', 'country': 'Russia', 'state': 'Nizhny Novgorod'},
            
            ]
    for item in cities:
        # crawl_things_to_do_city(db, item)
        crawl_resturant_city(db, item)
    return

if __name__ == "__main__":
    main()
