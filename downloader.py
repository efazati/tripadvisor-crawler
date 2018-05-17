import os
from pymongo import MongoClient
import requests

root = 'images/'

def get_db():
    client = MongoClient()
    db = client['world']
    return db

def download_image(url, path):
    f = open('%s.jpg' % path,'wb')
    print('get => ', url)
    f.write(requests.get(url).content)
    f.close()

def main():
    for x in xrange(1,10):
        try:
            db = get_db()
            for item in db.location.find(no_cursor_timeout=False):
                directory = root + str(item['_id'])
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    index = 1
                    for image in item['images']:
                        download_image(image, '%s/%s' % (directory, index))
                        index += 1
        except:
            pass

if __name__ == "__main__":
    main()