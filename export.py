import simplekml
from pymongo import MongoClient

def generate_map(name):
    def get_db():
        client = MongoClient()
        db = client['world']
        return db

    db = get_db()

    todo = {}
    resturant = {}
    todo['all'] =simplekml.Kml()
    todo['top'] =simplekml.Kml()
    resturant['all'] =simplekml.Kml()
    resturant['top'] =simplekml.Kml()

    points = db.location.find({'country': name})
    for point in points:
        try:
            rank = int(point['popularity'].split(' ')[0].replace('#', ''))
        except:
            rank = 999
        if rank > 100:
            continue
        if point['type'] == 'resturant':
            kml_instance = resturant
        else:
            kml_instance = todo
        if rank < 15:
            kml_instance = kml_instance['top']
        else:
            kml_instance = kml_instance['all']

        images = ''
        index = 1
        for image in point['images']:
            images += "<img src='http://iranatrip.com/world/%s/%s.jpg' />" % (image, index)
            index += 1
        description = """%s
        <br/>
        %s <br/>
        %s <br/>
        %s <br/>
        %s <br/><br/>
        %s <br/><br/>
        %s
        """ % (images, point['popularity'], point['hours'], point['phone'], point['address'], point['description'], point['url'])
        kml_instance.newpoint(name='%s - %s' % (point['name'], rank), coords=[(point['location']['long'],point['location']['lat'])], description=description)

    todo['all'].save("kml/%s_todo_all.kml" % name)
    todo['top'].save("kml/%s_todo_top.kml" % name)
    resturant['all'].save("kml/%s_resturant_all.kml" % name)
    resturant['top'].save("kml/%s_resturant_top.kml" % name)


if __name__ == "__main__":
    for i in ['Russia', 'Georgia', 'Armenia', 'Turkey', 'Malaysia']:
        generate_map(i)
