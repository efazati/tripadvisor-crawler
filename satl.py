from os import makedirs, path, symlink, listdir, stat
import hashlib
import jsonplus as json
import datetime
import shutil


class NotFound(Exception):
    pass


class KeyRequired(Exception):
    pass


class Satl(object):
    """In persian bucket is Satl
    In this utility you can save documents in files without any dependencies
    """

    store_path = 'satl'
    data_path = store_path + '/data'
    keyword_path = store_path + '/keywords'

    def __init__(self, key=None, _id=None, data=None):
        if key:
            self._id = 'satl_' + self.key_generate(key)
        elif _id:
            self._id = _id
        else:
            # @TODO maybe in future generate _id can be helpfull
            raise KeyRequired
        if data:
            self.data = data
        else:
            self.data = {}


    @property
    def path(self):
        return self.get_path(_id=self._id)

    def update_date(self):
        return datetime.fromtimestamp(stat(self.path).st_ctime)

    def create_date(self):
        return datetime.fromtimestamp(stat(self.path).st_mtime)

    @property
    def pk(self):
        return self._id

    @classmethod
    def keyword_path(cls, keyword):
        return '%s/%s' % (cls.keyword_path, cls.key_generate(keyword))

    @classmethod
    def get_path(cls, key=None, _id=None):
        if key and not _id:
            _id = cls.key_generate(key)
        return '%s/%s' % (cls.data_path, _id)

    def set_keywords(self, keywords):
        self.keywords = keywords

    def set_data(self, data):
        self.data = data

    def relate_keyword(self, keyword):
        keyword_path = self.keyword_path(keyword)

        if not path.exists(keyword_path):
            makedirs('%s/' % keyword_path)

        symlink(self.path, keyword_path)

    def unrelate_keyword(self, keyword):
        raise NotImplementedError

    def rerelate_keywords(self):
        raise NotImplementedError

    def _prepare_storage(self):
        if not path.exists(self.store_path):
            makedirs(self.store_path)

        if not path.exists(self.data_path):
            makedirs('%s/' % self.data_path)

        if not path.exists(self.path):
            makedirs('%s/' % self.path)

    def save(self):
        self._prepare_storage()
        with open('%s/data.json' % self.path, 'w') as f:
            f.write(json.dumps(self.data))

    def attach_file_object(self, file_body, name):
        self._prepare_storage()

        if not path.exists(self.path + '/files'):
            makedirs(self.path + '/files')

        f = open('%s/files/%s' % (self.path, name), 'wb')
        f.write(file_body)
        f.close()

    def attach_file_path(self, file_path):
        self._prepare_storage()

        if not path.exists(self.path + '/files'):
            makedirs(self.path + '/files')

        shutil.copy2(file_path, self.path + '/files/')

    def files(self):
        self._prepare_storage()
        path_file = self.path + '/files/'
        if not path.exists(path_file):
            makedirs(path_file)
        return self._query(path_file)

    def count_files(self):
        self._prepare_storage()
        path_file = self.path + '/files/'
        if not path.exists(path_file):
            makedirs(path_file)
        return len(listdir(path_file))

    def load(self):
        path_file = '%s/data.json' % self.path
        if not path.exists(path_file):
            raise NotFound
        with open(path_file, 'r') as f:
            data = json.loads(f.read())
            self.data = data
            return self.data

    def get(self, key, force_get=False):
        if self.data == {} or force_get:
            self.load()
        return self.data[key]

    @classmethod
    def _query(cls, path_file):
        for item in listdir(path_file):
            yield Satl(_id=item)

    @classmethod
    def is_exists(cls, _id):
        path_file = cls.get_path(_id)
        if not path.exists(path_file):
            return False
        return True

    @classmethod
    def filter_by_keyword(cls, keyword):
        path_file = cls.keyword_path(keyword)
        if not path.exists(path_file):
            raise NotFound
        return cls._query(path_file)

    @classmethod
    def filter_by_date(cls, keyword):
        raise NotImplementedError

    @classmethod
    def all(cls):
        path_file = '%s/%s' % (cls.store_path, cls.data_path)
        if not path.exists(path_file):
            makedirs('%s' % path_file)
        return cls._query(path_file)

    @staticmethod
    def key_generate(key):
        return hashlib.sha1(key).hexdigest()
