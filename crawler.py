from datetime import datetime
from time import sleep
import requests
from satl import Satl
from bs4 import BeautifulSoup
import re

from utils.printer import printer

base_url = 'https://www.tripadvisor.com'
top_activity_url = base_url + '/Attractions-%s-%sActivities-%s.html'
top_restaurants_url = base_url + '/Restaurants-%s-%sActivities-%s.html'

def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    printer('blue', 'Get', url)
    try:
        html = requests.get(url, headers=headers)
    except:
        pass
    sleep(1)
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
    printer('yellow', kind, '%s - %s' % (data_dict['country'], data_dict['state']))
    return data_dict


def get_poi_list(url, crawler_list, kind):
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
        if is_exists(url):
            continue
        poi_data = ''
        if url.endswith('html.html'):
            printer('yellow', 'Not download', url)
            continue
        try:
            poi_data = get_poi(url, poi, crawler_list, kind)
        except Exception as e:
            msg = '%s - %s' % (url, e)
            printer('red', 'Error', msg)
        if poi_data:
            set_data(poi_data)
    return pois


def make_pages_and_normalize_input(loop, keys):
    if loop == 0:
        page = ''
    else:
        page = 'oa%s-' % (loop * 30)

    if 'state' in keys:
        state = keys['state']
    else:
        state = keys['country']

    printer('green', 'Country', keys['country'])

    if 'name' in keys:
        name = keys['name']
    else:
        name = keys['country']

    return page, state, name


def get_images(satl_obj):
    count = satl_obj.count_files()
    if count != 0:
        return False
    index = 1
    for url in satl_obj.get('images'):
        printer('cyan', 'Download', url)
        try:
            img = requests.get(url)
            satl_obj.attach_file_object(img.content, '%s.jpg' % index)
        except:
            pass
        index += 1
    return True


def crawl_things_to_do_city(keys):
    for x in xrange(0, 6):
        page, state, name = make_pages_and_normalize_input(x, keys)
        url = top_activity_url % (keys['index'], page, name)
        get_poi_list(url, keys, 'things-to-do')
    return True


def crawl_resturant_city(keys):
    for x in xrange(0, 1):
        page, state, name = make_pages_and_normalize_input(x, keys)
        url = top_restaurants_url % (keys['index'], page, keys['name'])
        get_poi_list(url, keys, 'resturant')
    return True


def get_detail_of_city(keys):
    crawl_resturant_city(keys)
    crawl_things_to_do_city(keys)


def get_cities(keys):
    url = top_activity_url % (keys['index'], '', keys['country'])

    page = get_page(url)
    sidebar = page.find_all('div', class_='navigation_list')
    elements = sidebar[1].find_all('div', class_='ap_navigator')
    items = []
    for element in elements:
        url_bones = element.find('a').get('href').split('-')
        if len(url_bones) == 4:
            name = url_bones[3].replace('.html', '')
        else:
            name = url_bones[4].replace('.html', '')
        items.append(
            {'index': url_bones[1], 'name': url_bones[3], 'state': get_text(element).replace('Things to do in ', ''),
             'country': keys['country']})

    return items


def is_exists(url):
    return Satl.is_exists(url)


def set_data(data):
    # if is_exists(data['url']):
    #     return False
    data['create_date'] = datetime.now()
    data['updated'] = False
    satl = Satl(data['url'], data=data)
    printer('magenta', 'Save', " %s - %s" % (satl.pk, satl.get('name')))
    satl.save()
    get_images(satl)
    

    # this part writen beacuse of update images
    # else:
    #     satl = Satl(data['url']).load()
    return False

 
def main():
    countries = [
        # {'index': 'g293998', 'country': 'Iran'},
        # {'index': 'g293860', 'country': 'India'},
        # {'index': 'g294459', 'country': 'Russia'},
        # {'index': 'g294211', 'country': 'China'},
        # {'index': 'g187275', 'country': 'Germany'},
        # {'index': 'g187768', 'country': 'Italy'},
        # {'index': 'g293969', 'country': 'Turkey'},
        # {'index': 'g187427', 'country': 'Spain'}, 
        # {'index': 'g187070', 'country': 'France'},
        # {'index': 'g293951', 'country': 'Malaysia'},
        {'index': 'g293915', 'country': 'Thailand'},
    ]
    cities = []
    for country in countries:
        cities += get_cities(country)

    for item in cities:
        get_detail_of_city(item)
    return


if __name__ == "__main__":
    main()
