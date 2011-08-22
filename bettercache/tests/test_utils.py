import time
from unittest2 import TestCase

import mock

# from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.utils.http import http_date

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


    @mock.patch('bettercache.utils.settings')
    def test_should_cache(self, settings):
        self.set_settings(settings)
        req = HttpRequest()
        req._cache_update_cache = True
        req.session = mock.Mock()
        req.session.accessed = False
        req.user = mock.Mock()
        req.user.is_authenticated = False
        resp = HttpResponse()
        resp.status_code = 200
        settings.BETTERCACHE_ANONYMOUS_ONLY = False
        cm = CachingMixin()
        self.assertTrue(cm.should_cache(req, resp))
        settings.BETTERCACHE_ANONYMOUS_ONLY = True
        self.assertTrue(cm.should_cache(req, resp))
        req.session.accessed = True
        self.assertTrue(cm.should_cache(req, resp))
        req.user.is_authenticated = True
        self.assertFalse(cm.should_cache(req, resp))
        settings.BETTERCACHE_ANONYMOUS_ONLY = False
        resp.status_code=500
        self.assertFalse(cm.should_cache(req, resp))
        resp.status_code=200
        req._cache_update_cache = False 
        self.assertFalse(cm.should_cache(req, resp))

    def test_uncacheable_headers(self):
        resp = HttpResponse()
        cm = CachingMixin()
        self.assertFalse(cm.has_uncacheable_headers(resp))
        resp['Expires'] = http_date(time.time()-100)
        self.assertTrue(cm.has_uncacheable_headers(resp))
        resp['Expires'] = http_date(time.time()+100000)
        self.assertFalse(cm.has_uncacheable_headers(resp))
        cc_dict = { 'max-age' : 0,}
        set_header_dict(resp, 'Cache-Control', cc_dict)
        self.assertTrue(cm.has_uncacheable_headers(resp))
        cc_dict['max-age'] = 100
        set_header_dict(resp, 'Cache-Control', cc_dict)
        self.assertFalse(cm.has_uncacheable_headers(resp))
        cc_dict['no-cache'] = True
        set_header_dict(resp, 'Cache-Control', cc_dict)
        self.assertTrue(cm.has_uncacheable_headers(resp))
        cc_dict.pop('no-cache')
        cc_dict['private'] = True
        set_header_dict(resp, 'Cache-Control', cc_dict)
        self.assertTrue(cm.has_uncacheable_headers(resp))
