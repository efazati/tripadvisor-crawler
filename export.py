from os import path, makedirs
import simplekml
from satl import Satl
import shutil


def main(small_version=True):
    maps = {}
    print(Satl.count())
    for satl in Satl.all():
        point = satl.load()
        if point['country'] not in maps:
            maps[point['country']] = {'resturant': {'top': simplekml.Kml(), 'medium': simplekml.Kml(), 'low': simplekml.Kml()},
                                    'todo': {'top': simplekml.Kml(), 'medium': simplekml.Kml(), 'low': simplekml.Kml()},
                                    }

        try:
            rank = int(point['popularity'].split(' ')[0].replace('#', ''))
        except:
            rank = 999
        # if rank > 100:
        #     continue
        if point['type'] == 'resturant':
            kml_instance = maps[point['country']]['resturant']
        else:
            kml_instance = maps[point['country']]['todo']
        if rank < 15:
            kml_instance = kml_instance['top']
        elif rank < 80:
            kml_instance = kml_instance['medium']
        else:
            kml_instance = kml_instance['low']

        images = ''
        if small_version:
            try:
                if point['images']:
                    folder = 'kml/%s/images/' % point['country']
                    if not path.exists(folder):
                        makedirs(folder)
                    try:
                        shutil.copy('satl/data/%s/files/1.jpg' % satl.pk, '%s/%s.jpg' % (folder, satl.pk))
                    except:
                        shutil.copy('satl/data/%s/files/2.jpg' % satl.pk, '%s/%s.jpg' % (folder, satl.pk))

                    images += "<img src='http://iranatrip.com/world/kml/%s/images/%s.jpg' />" % (point['country'], satl.pk)
            except:
                pass

        else:
            index = 1
            for image in point['images']:
                images += "<img src='http://iranatrip.com/world/%s/files/%s.jpg' />" % (satl.pk, index)
                index += 1

        comment = ''
        if 'comment' in point:
            comment = point['comment']
        description = """%s
        <br/>
        %s <br/>
        %s <br/>
        %s <br/>
        %s <br/><br/>
        %s <br/><br/>
        %s
         <br/><br/>
         %s
        """ % (images, point['popularity'], point['hours'], point['phone'], point['address'], point['description'],
               comment, point['url'])
        kml_instance.newpoint(name='%s - %s' % (point['name'], rank),
                              coords=[(point['location']['long'], point['location']['lat'])], description=description)

    for key, value in maps.items():
        folder = 'kml/%s' % key
        if not path.exists(folder):
            makedirs(folder)
        for kind in ['resturant', 'todo']:
            for level in ['top', 'medium', 'low']:
                value[kind][level].save("%s/%s_%s.kml" % (folder, kind, level))


if __name__ == "__main__":
    main()