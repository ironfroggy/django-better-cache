from django.test import TestCase
from django.core.cache import cache

class FakeCache(object):

    def __init__(self):
        self.store = {}
        self.set_keys = []
        self.deleted_keys = []


    def get(self, key, val, default=None, **kwargs):
        try:
            return self.store[key]
        except KeyError:
            return default

    def set(self, key, val, timeout=None, **kwargs):
       self.store[key] = val
       if not key in self.set_keys:
           self.set_keys += key

    def add(self, key, val, timeout=None, **kwargs):
        if not key in self.store:
            self.store[key] = val
            if not key in self.set_keys:
               self.set_keys += key
            return True
        return False

    def delete(self, key, **kwargs):
        try:
            self.store.pop(key)
        except KeyError:
            pass
        if not key in self.deleted_keys:
            self.deleted_keys += key

    def clear(self):
        self.store = {}



class CachingTestMeta(type):
   def __new__(cls, name, bases, attrs):
        try:
            setFun = attrs.pop('setFun')
        except KeyError:
            raise Exception("A Caching test case must have a setFun")
        try:
            oldsetUp = attrs.pop('setUp')
        except KeyError:
            attrs['setUp'] = setFun
            attrs['setUp'].__name__ = 'setUp'
        else:
            def setUp(self):
                oldsetUp(self)
                self.real_cache = cache
                cache = FakeCache()
                setFun(self)
                self.tracked_keys = [key for key in cache.set_keys if self.keyre.search(key)]
                if not self.tracked_keys:
                    raise Exception("You're setFun did not set any keys this test isn't testing anything")
                cache.set_keys = []

            attrs['setUp'] = setUp

        try:
            oldtearDown = attrs.pop('tearDown')
        except KeyError:
            def tearDown(self):
                cache = self.real_cache
            attrs['tearDown'] = tearDown
        else:
            def tearDown(self):
                oldtearDown(self)
                cache = self.real_cache
            attrs['tearDown'] = tearDown

        def check_keys(self, accept_del=True):
            changed_keys = cache.set_keys
            if accept_del:
                changed_keys += cache.deleted_keys
            for key in expected_keys:
                self.assertTrue(key in changed_keys) #TODO: make this explicit when it fails

        nattrs = {}
        for key, val in attrs.items():
            if callable(val) and key[:4] == 'test':
                testfun = attrs.pop(key) #This appears safe
                    
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
    __metaclass__ = CachingTestMeta
    def setFun(self):
        pass
