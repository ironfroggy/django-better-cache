from unittest import TestCase
import mock
from bettercache.middleware import BetterCacheMiddleware 


class TestMiddleware(TestCase):

    def test_req(self):
        request = mock.Mock()
        request.method = 'POST'
        request._cache_update_cache = False
        request.META = {'HTTP_CACHE_CONTROL' : ''}
        bcm = BetterCacheMiddleware()
        self.assertEqual(bcm.process_request(request), None)
        self.assertFalse(request._cache_update_cache)
        request.method = 'GET'
        request._cache_update_cache = False
        bcm.get_cache = lambda x: (None, None,)
        self.assertEqual(bcm.process_request(request), None)
        self.assertTrue(request._cache_update_cache)


    def test_celery_throttling(self):
        '''test to make sure we don't regenerate in the case of a fresh page
        existing in cache when a pagegen task tries to run'''
        request = mock.Mock()
        request.method = 'GET'
        request._cache_update_cache = True
        request.META = {'HTTP_CACHE_CONTROL' : ''}

        bcm = BetterCacheMiddleware()
        bcm.get_cache = lambda x: (True, True,)
        bcm.should_regenerate = lambda x: True
        self.assertEqual(bcm.process_request(request), None)
        bcm.should_regenerate = lambda x: False
        self.assertTrue(bcm.process_request(request))
