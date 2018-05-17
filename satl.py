import os
import hashlib
import jsonplus as json

class NotFound(Exception):
    pass

class KeyRequired(Exception):
    pass

class Satl(object):
    """In persian bucket is Satl"""

    store_path = 'satl'
    data_path = store_path + '/data'
    keyword_path = store_path + '/keywords'

    def __init__(self, key=None, _id=None, data=None):
        if key:
            self._id = 'satl_'+ self.key_generate(key)
        elif _id:
            self._id = _id
        else:
            # @TODO maybe in future generate _id can be helpfull
            raise KeyRequired
        if data:
            self.data = data
        else:
            self.data = {}

    @classmethod
    def get_path(cls, key=None, _id=None):
        if key and not _id:
            _id = cls.key_generate(key)
        return '%s/%s' % (cls.data_path, _id)

    @property
    def path(self):
        return self.get_path(_id=self._id)

    @classmethod
    def keyword_path(cls, keyword):
        return '%s/%s' % (cls.keyword_path, cls.key_generate(keyword))

    def set_keywords(self, keywords):
        self.keywords = keywords

    def set_data(self, data):
        self.data = data

    def relate_keyword(self, keyword):
        keyword_path = self.keyword_path(keyword)

        if not os.path.exists(keyword_path):
            os.makedirs('%s/' % keyword_path)

        os.symlink(self.path, keyword_path)

    def unrelate_keyword(self, keyword):
        raise NotImplementedError

    def _prepare_storage(self):
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)

        if not os.path.exists(self.data_path):
            os.makedirs('%s/' % self.data_path)

        if not os.path.exists(self.path):
            os.makedirs('%s/' % self.path)

    def save(self):
        self._prepare_storage()        
        with open('%s/data.json' % self.path, 'w') as f:
            f.write(json.dumps(self.data))
    
    def attach_file(self, f, name):
        pass
    def load(self):
        with open('%s/data.json' % self.path, 'r') as f:
            data = json.loads(f.read())
            self.data = data 
            return self.data 
        raise NotFound

    def get(self, key, force_get=False):
        if self.data == {} or force_get:
            self.load
        return self.data['key']

    def _query(self, path):
        for item in listdir(path):
            yield Stal(enc_key=item)

    @classmethod
    def is_exists(cls, _id):
        path = cls.get_path(_id)
        if not os.path.exists(path):
            return False
        return True

    @classmethod
    def filter(cls, keyword):
        path = cls.keyword_path(keyword)
        if not os.path.exists(path):
            raise NotFound
        cls._query(path)

    @classmethod
    def all(cls, keyword):
        path = '%s/%s' % (cls.store_path, cls.data_path)
        if not os.path.exists(path):
            os.makedirs('%s' % path)
        cls._query(path)

    @staticmethod
    def key_generate(key):
        return hashlib.sha1(key).hexdigest()
