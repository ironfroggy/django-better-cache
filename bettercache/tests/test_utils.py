import time
from datetime import timedelta
from unittest import TestCase

import mock

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.utils.http import http_date, parse_http_date

from bettercache.utils import get_header_dict, set_header_dict, CachingMixin

class FakeCache(object):

    def __init__(self):
        self.store = {}

    def get(self, key, val, default=None, **kwargs):
        try:
            return self.store[key]
        except KeyError:
            return default

    def set(self, key, val, timeout=None, **kwargs):
        self.store[key] = val

    def delete(self, key, **kwargs):
        try:
            self.store.pop(key)
        except KeyError:
            pass
    def clear(self):
        self.store = {}

#TODO: there must be a better way to mock this
fake_cache = FakeCache()

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
        settings.BETTERCACHE_CACHEABLE_STATUS = [200,]

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

    @mock.patch('bettercache.utils.settings')
    @mock.patch('bettercache.utils.cache', new=fake_cache)
    def test_get_cache(self, settings):
        fake_cache.clear()
        self.set_settings(settings)
        req = HttpRequest()
        cm = CachingMixin()
        cm.cache_key = lambda x: 'notcachedyet'
        self.assertEquals(cm.get_cache(req), (None, None))
        cm.cache_key = lambda x: 'test_key'
        self.assertEquals(cm.get_cache(req), (None, None))
        fake_cache.set('test_key', ('resp', time.time() - 3600)) 
        self.assertEquals(cm.get_cache(req), ('resp', True))
        fake_cache.set('test_key', ('resp', time.time() + 3600)) 
        self.assertEquals(cm.get_cache(req), ('resp', False))

    @mock.patch('bettercache.utils.cache')
    @mock.patch('bettercache.utils.settings')
    def test_set_cache(self, settings,  cache):
        resp = mock.Mock()
        req = mock.Mock()
        cm = CachingMixin()
        cm.cache_key = lambda x: 'test'
        resp.render = False
        cm.set_cache(req, resp)
        self.assertTrue(cache.set.called)
        resp.render = lambda : 1
        cm.set_cache(req, resp)
        self.assertTrue(resp.add_post_render_callback.called)

    def test_bypass_cache(self):
        req = mock.Mock()
        req.META = {'HTTP_CACHE_CONTROL' : 'max-age=0'}
        cm = CachingMixin()
        self.assertFalse(cm.should_bypass_cache(req))
        req.META['HTTP_CACHE_CONTROL'] = 'max-age=0, no-cache'
        self.assertTrue(cm.should_bypass_cache(req))

    @mock.patch('bettercache.utils.time')
    def test_should_regenerate(self, mocktime):
        now = 1319128343
        mocktime.time.return_value = now
        cm = CachingMixin()
        response = HttpResponse()
        response['Last-Modified'] = http_date(now)
        self.assertFalse(cm.should_regenerate(response))
        response['Last-Modified'] = http_date(now - (100 + settings.BETTERCACHE_LOCAL_POSTCHECK))
        self.assertTrue(cm.should_regenerate(response))
