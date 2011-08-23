from unittest2 import TestCase
import mock
from bettercache.middleware import BetterCacheMiddleware 


class TestMiddleware(TestCase):
    
    @mock.patch('bettercache.middleware.GeneratePage')
    @mock.patch('bettercache.middleware.CachingMixin')
    def test_req(self, GM, CM):
        request = mock.Mock()
        request.method = 'POST'
        bcm = BetterCacheMiddleware()
        self.assertEqual(bcm.process_request(request), None)
        self.assertFalse(request._cache_update_cache)
        request.method = 'GET'
        CM.get_cache.return_value = (None, None,)
        self.assertEqual(bcm.process_request(request), None)
        self.assertTrue(request._cache_update_cache)
        # CM.get_cache.return_value = ('RESP', True,)
        # self.assertEqual(bcm.process_request(request), 'RESP')
        # self.assertFalse(request._cache_update_cache)
        # self.assertTrue(GM.apply_async.called)
