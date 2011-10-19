from bettercache.tasks import GeneratePage
from bettercache.utils import CachingMixin, strip_wsgi


class TestAsyncMiddleware(object):
    """ Does not deal with middleware sideeffects """
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD',) or CachingMixin.should_bypass_cache(request):
            return None
        if hasattr(request, '_cache_update_cache'):
            return None
        request._cache_update_cache = False
        result = GeneratePage.apply_async((strip_wsgi(request),))
        response = result.get()
        return response


class BetterCacheMiddleware(CachingMixin):
    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        celery_task = False
        if getattr(request, '_cache_update_cache', False):
            celery_task = True
        if not request.method in ('GET', 'HEAD'):
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        request._cache_update_cache = True
        if self.should_bypass_cache(request):
            return None

        response, expired = self.get_cache(request)

        if response is None:
            return None # No cache information available, need to rebuild.

        # TODO: this logic should be in the task not here but it needs the per_request_middleware
        if celery_task:
            if self.should_regenerate(response):
                return None
        elif expired:
            GeneratePage.apply_async((strip_wsgi(request),))
            self.set_cache(request, response)
        # don't update right since we're serving from cache
        request._cache_update_cache = False

        return response

    def process_response(self, request, response):
        """ Sets the cache and deals with caching headers if needed
        """
        if not self.should_cache(request, response):
            # We don't need to update the cache, just return
            return response 

        response = self.patch_headers(response)
        self.set_cache(request, response)

        return response
