import re
from django.core.cache import cache
from bettercache.testing import CachingTestCase


class CachingTestCaseTestCase(CachingTestCase):
    """ a simple test of CachingTestCase """
    keyre = re.compile('foo')

    def setFun(self):
        cache.set('foo', 1)

    def test_inval(self):
        cache.delete('foo')
