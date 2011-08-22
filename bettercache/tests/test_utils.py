from unittest2 import TestCase

import mock

# from django.conf import settings
from django.http import HttpResponse

from bettercache.utils import get_header_dict, set_header_dict, CachingMixin

class TestDict(TestCase):
    def test_get_dict(self):
        resp = HttpResponse()
        resp['Cache-Control'] = 'x=1, y'
        expected = dict(x='1', y=True)
        actual = get_header_dict(resp, 'Cache-Control')
        for k in expected:
            self.assertEqual(expected[k], actual[k])

    def test_no_dict(self):
        resp = HttpResponse()
        self.assertEqual(get_header_dict(resp, 'Cache-Control'), {})

    def test_set_dict(self):
        resp = HttpResponse()
        ccdict = dict(x='1', y=True)
        set_header_dict(resp, 'Cache-Control', ccdict)
        self.assertEqual(resp['Cache-Control'], 'y, x=1')


class TestCachingMixin(TestCase):


    def set_settings(self, settings): 
        settings.BETTERCACHE_ANONYMOUS_ONLY = False
        settings.BETTERCACHE_EDGE_MAXAGE = '1d'
        settings.BETTERCACHE_CACHE_MAXAGE = 60
        settings.BETTERCACHE_EDGE_POSTCHECK_RATIO = .1
        settings.BETTERCACHE_LOCAL_POSTCHECK = 60 

    @mock.patch('bettercache.utils.settings')
    def test_patch_headers(self, settings):
        resp = HttpResponse()
        resp['Vary'] = 'cookie, accept-encoding'
        self.set_settings(settings)
        cm = CachingMixin()
        cm.patch_headers(resp)
        self.assertEqual(resp['Vary'], 'accept-encoding')
        self.assertEqual(resp['Edge-Control'], 'cache-maxage=1d')
        ccdict = get_header_dict(resp, 'Cache-Control')
        self.assertEqual(ccdict['pre-check'], '60')
        self.assertEqual(ccdict['post-check'], '6')
        self.assertEqual(ccdict['max-age'], '60')
