# -*- coding: utf-8 -*-

# Unit tests for cache middleware copied from django

import os
import tempfile
import time
import warnings

from django.conf import settings
from django.core import management
from django.core.cache import get_cache, DEFAULT_CACHE_ALIAS
from django.core.cache.backends.base import CacheKeyWarning
from django.http import HttpResponse, HttpRequest, QueryDict
from django.middleware.cache import FetchFromCacheMiddleware, UpdateCacheMiddleware, CacheMiddleware
from django.test import RequestFactory
from django.test.utils import get_warnings_state, restore_warnings_state
from django.utils import translation
from django.utils import unittest
from django.utils.cache import patch_vary_headers, get_cache_key, learn_cache_key
from django.utils.hashcompat import md5_constructor
from django.views.decorators.cache import cache_page


def hello_world_view(request, value):
    return HttpResponse("Hello World %s" % value)

class CacheMiddlewareTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.orig_cache_middleware_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.orig_cache_middleware_key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.orig_cache_middleware_seconds = settings.CACHE_MIDDLEWARE_SECONDS
        self.orig_cache_middleware_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
        self.orig_caches = settings.CACHES

        settings.CACHE_MIDDLEWARE_ALIAS = 'other'
        settings.CACHE_MIDDLEWARE_KEY_PREFIX = 'middlewareprefix'
        settings.CACHE_MIDDLEWARE_SECONDS = 30
        settings.CACHE_MIDDLEWARE_ANONYMOUS_ONLY = False
        settings.CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            },
            'other': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'other',
                'TIMEOUT': '1'
            }
        }

    def tearDown(self):
        settings.CACHE_MIDDLEWARE_ALIAS = self.orig_cache_middleware_alias
        settings.CACHE_MIDDLEWARE_KEY_PREFIX = self.orig_cache_middleware_key_prefix
        settings.CACHE_MIDDLEWARE_SECONDS = self.orig_cache_middleware_seconds
        settings.CACHE_MIDDLEWARE_ANONYMOUS_ONLY = self.orig_cache_middleware_anonymous_only
        settings.CACHES = self.orig_caches

    def test_constructor(self):
        """
        Ensure the constructor is correctly distinguishing between usage of CacheMiddleware as
        Middleware vs. usage of CacheMiddleware as view decorator and setting attributes
        appropriately.
        """
        # If no arguments are passed in construction, it's being used as middleware.
        middleware = CacheMiddleware()

        # Now test object attributes against values defined in setUp above
        self.assertEqual(middleware.cache_timeout, 30)
        self.assertEqual(middleware.key_prefix, 'middlewareprefix')
        self.assertEqual(middleware.cache_alias, 'other')
        self.assertEqual(middleware.cache_anonymous_only, False)

        # If arguments are being passed in construction, it's being used as a decorator.
        # First, test with "defaults":
        as_view_decorator = CacheMiddleware(cache_alias=None, key_prefix=None)

        self.assertEqual(as_view_decorator.cache_timeout, 300) # Timeout value for 'default' cache, i.e. 300
        self.assertEqual(as_view_decorator.key_prefix, '')
        self.assertEqual(as_view_decorator.cache_alias, 'default') # Value of DEFAULT_CACHE_ALIAS from django.core.cache
        self.assertEqual(as_view_decorator.cache_anonymous_only, False)

        # Next, test with custom values:
        as_view_decorator_with_custom = CacheMiddleware(cache_anonymous_only=True, cache_timeout=60, cache_alias='other', key_prefix='foo')

        self.assertEqual(as_view_decorator_with_custom.cache_timeout, 60)
        self.assertEqual(as_view_decorator_with_custom.key_prefix, 'foo')
        self.assertEqual(as_view_decorator_with_custom.cache_alias, 'other')
        self.assertEqual(as_view_decorator_with_custom.cache_anonymous_only, True)

    def test_middleware(self):
        middleware = CacheMiddleware()
        prefix_middleware = CacheMiddleware(key_prefix='prefix1')
        timeout_middleware = CacheMiddleware(cache_timeout=1)

        request = self.factory.get('/view/')

        # Put the request through the request middleware
        result = middleware.process_request(request)
        self.assertEqual(result, None)

        response = hello_world_view(request, '1')

        # Now put the response through the response middleware
        response = middleware.process_response(request, response)

        # Repeating the request should result in a cache hit
        result = middleware.process_request(request)
        self.assertNotEquals(result, None)
        self.assertEqual(result.content, 'Hello World 1')

        # The same request through a different middleware won't hit
        result = prefix_middleware.process_request(request)
        self.assertEqual(result, None)

        # The same request with a timeout _will_ hit
        result = timeout_middleware.process_request(request)
        self.assertNotEquals(result, None)
        self.assertEqual(result.content, 'Hello World 1')

    def test_cache_middleware_anonymous_only_wont_cause_session_access(self):
        """ The cache middleware shouldn't cause a session access due to
        CACHE_MIDDLEWARE_ANONYMOUS_ONLY if nothing else has accessed the
        session. Refs 13283 """
        settings.CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware

        middleware = CacheMiddleware()
        session_middleware = SessionMiddleware()
        auth_middleware = AuthenticationMiddleware()

        request = self.factory.get('/view_anon/')

        # Put the request through the request middleware
        session_middleware.process_request(request)
        auth_middleware.process_request(request)
        result = middleware.process_request(request)
        self.assertEqual(result, None)

        response = hello_world_view(request, '1')

        # Now put the response through the response middleware
        session_middleware.process_response(request, response)
        response = middleware.process_response(request, response)

        self.assertEqual(request.session.accessed, False)

    def test_cache_middleware_anonymous_only_with_cache_page(self):
        """CACHE_MIDDLEWARE_ANONYMOUS_ONLY should still be effective when used
        with the cache_page decorator: the response to a request from an
        authenticated user should not be cached."""
        settings.CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

        request = self.factory.get('/view_anon/')

        class MockAuthenticatedUser(object):
            def is_authenticated(self):
                return True

        class MockAccessedSession(object):
            accessed = True

        request.user = MockAuthenticatedUser()
        request.session = MockAccessedSession()

        response = cache_page(hello_world_view)(request, '1')

        self.assertFalse("Cache-Control" in response)

    def test_view_decorator(self):
        # decorate the same view with different cache decorators
        default_view = cache_page(hello_world_view)
        default_with_prefix_view = cache_page(key_prefix='prefix1')(hello_world_view)

        explicit_default_view = cache_page(cache='default')(hello_world_view)
        explicit_default_with_prefix_view = cache_page(cache='default', key_prefix='prefix1')(hello_world_view)

        other_view = cache_page(cache='other')(hello_world_view)
        other_with_prefix_view = cache_page(cache='other', key_prefix='prefix2')(hello_world_view)
        other_with_timeout_view = cache_page(4, cache='other', key_prefix='prefix3')(hello_world_view)

        request = self.factory.get('/view/')

        # Request the view once
        response = default_view(request, '1')
        self.assertEqual(response.content, 'Hello World 1')

        # Request again -- hit the cache
        response = default_view(request, '2')
        self.assertEqual(response.content, 'Hello World 1')

        # Requesting the same view with the explicit cache should yield the same result
        response = explicit_default_view(request, '3')
        self.assertEqual(response.content, 'Hello World 1')

        # Requesting with a prefix will hit a different cache key
        response = explicit_default_with_prefix_view(request, '4')
        self.assertEqual(response.content, 'Hello World 4')

        # Hitting the same view again gives a cache hit
        response = explicit_default_with_prefix_view(request, '5')
        self.assertEqual(response.content, 'Hello World 4')

        # And going back to the implicit cache will hit the same cache
        response = default_with_prefix_view(request, '6')
        self.assertEqual(response.content, 'Hello World 4')

        # Requesting from an alternate cache won't hit cache
        response = other_view(request, '7')
        self.assertEqual(response.content, 'Hello World 7')

        # But a repeated hit will hit cache
        response = other_view(request, '8')
        self.assertEqual(response.content, 'Hello World 7')

        # And prefixing the alternate cache yields yet another cache entry
        response = other_with_prefix_view(request, '9')
        self.assertEqual(response.content, 'Hello World 9')

        # Request from the alternate cache with a new prefix and a custom timeout
        response = other_with_timeout_view(request, '10')
        self.assertEqual(response.content, 'Hello World 10')

        # But if we wait a couple of seconds...
        time.sleep(2)

        # ... the default cache will still hit
        cache = get_cache('default')
        response = default_view(request, '11')
        self.assertEqual(response.content, 'Hello World 1')

        # ... the default cache with a prefix will still hit
        response = default_with_prefix_view(request, '12')
        self.assertEqual(response.content, 'Hello World 4')

        # ... the explicit default cache will still hit
        response = explicit_default_view(request, '13')
        self.assertEqual(response.content, 'Hello World 1')

        # ... the explicit default cache with a prefix will still hit
        response = explicit_default_with_prefix_view(request, '14')
        self.assertEqual(response.content, 'Hello World 4')

        # .. but a rapidly expiring cache won't hit
        response = other_view(request, '15')
        self.assertEqual(response.content, 'Hello World 15')

        # .. even if it has a prefix
        response = other_with_prefix_view(request, '16')
        self.assertEqual(response.content, 'Hello World 16')

        # ... but a view with a custom timeout will still hit
        response = other_with_timeout_view(request, '17')
        self.assertEqual(response.content, 'Hello World 10')

        # And if we wait a few more seconds
        time.sleep(2)

        # the custom timeouot cache will miss
        response = other_with_timeout_view(request, '18')
        self.assertEqual(response.content, 'Hello World 18')

if __name__ == '__main__':
    unittest.main()
