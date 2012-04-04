from django.test import TestCase

class FakeCache(object):

    def __init__(self):
        self.store = {}
        self.set_keys = []
        self.deleted_keys = []


    def get(self, key, default=None, **kwargs):
        try:
            return self.store[key]
        except KeyError:
            return default

    def set(self, key, val, timeout=None, **kwargs):
       self.store[key] = val
       if not key in self.set_keys:
           self.set_keys.append(key)

    def add(self, key, val, timeout=None, **kwargs):
        if not key in self.store:
            self.store[key] = val
            if not key in self.set_keys:
               self.set_keys.append(key)
            return True
        return False

    def delete(self, key, **kwargs):
        try:
            self.store.pop(key)
        except KeyError:
            pass
        if not key in self.deleted_keys:
            self.deleted_keys.append(key)

    def clear(self):
        self.store = {}


class CachingTestMeta(type):
   def __new__(cls, name, bases, attrs):
        oldsetUp = attrs.pop('setUp')
        setFun = attrs.pop('setFun')
        def setUp(self):
            self.cache = FakeCache()
            oldsetUp(self)
            setFun(self)
            self.tracked_keys = [key for key in self.cache.set_keys if self.keyre.search(key)]
            if not self.tracked_keys:
                raise Exception("No keys are being tracked this test isn't testing anything")
            self.cache.set_keys = []
            self.cache.deleted_keys = []

        attrs['setUp'] = setUp

        oldtearDown = attrs.pop('tearDown')
        def tearDown(self):
            oldtearDown(self)
        attrs['tearDown'] = tearDown

        def check_keys(self, accept_del=True):
            changed_keys = self.cache.set_keys
            if accept_del:
                changed_keys += self.cache.deleted_keys
            for key in self.tracked_keys:
                self.assertTrue(key in changed_keys) #TODO: make this explicit when it fails

        nattrs = {}
        for key, val in attrs.items():
            if callable(val) and key[:4] == 'test':
                testfun = attrs.pop(key)
                # args and kwargs probably aren't necessary
                def test_cache(self, *args, **kwargs):
                    testfun(self, *args, **kwargs)
                    check_keys(self)
                nattrs[key] = test_cache
                nattrs[key].__name__ = key
            else:
                nattrs[key] = val
        attrs = nattrs

        return super(CachingTestMeta, cls).__new__(cls, name, bases, attrs)


class CachingTestCase(TestCase):
    """ CachingTestCase is a specific test case for cache invalidation
        It should only include tests for cache invaldation.
        To use it define the following:
        keyre: a refular expression that describes the key or keys you want to test
        setFun(self): a function which will set the keys
        test_foo(self, *args, **kwargs) any number of functions that should reset or delete the tracked keys 
        setUp and tearDown can be defined as normal
    """
    __metaclass__ = CachingTestMeta

    def setFun(self):
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass
