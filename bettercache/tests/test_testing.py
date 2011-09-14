import re
import django.core.cache
from bettercache.testing import CachingTestCase


class CachingTestCaseTestCase(CachingTestCase):
    """ a simple test of CachingTestCase """
    keyre = re.compile('foo')
    cache_modules = [django.core.cache]

    def setUp(self):
        self.real_cache = django.core.cache.cache
        django.core.cache.cache = self.cache
    
    def tearDown(self):
      django.core.cache.cache = self.real_cache  

    def setFun(self):
        django.core.cache.cache.set('foo', 1)

    def test_inval(self):
        django.core.cache.cache.delete('foo')
