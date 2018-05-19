import os
import requests
from satl import Satl

def download_image(url, path):
    print('get => ', url)
    return requests.get(url).content

def main():
    for item in Satl.all():
        for image in item.get('images'):
            image_content = download_image(image)
            index += 1
            item.attach_file(image_content, '%s.jpg' % index)

if __name__ == "__main__":
    main()