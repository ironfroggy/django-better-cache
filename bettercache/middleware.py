from django.conf import settings
from django.middleware.cache import UpdateCacheMiddleware, FetchFromCacheMiddleware
from django.utils.cache import patch_response_headers, get_cache_key, get_max_age, learn_cache_key

from bettercache.utils import set_post_pre_check_headers

class BetterUpdateCacheMiddleware(UpdateCacheMiddleware):

    def set_headers(self, request, response):
        """ Hook for setting additional headers """
        set_post_pre_check_headers(response)
        response['Edge-control'] = "cache-maxage=270s"

    def process_response(self, request, response):
        """ Sets the cache, if needed.
            Copied from django so headers are only updated when appropriate.
        """                                                                             
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.                                                        
            return response                                                                                          
        if not response.status_code == 200:
            return response                                                                                          
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout                                        
        # length.                                                                                                    
        timeout = get_max_age(response)                                                                              
        if timeout == None:
            timeout = self.cache_timeout                                                                             
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        # This is the only difference from django for now
        self.set_headers(request, response)
        if timeout:
            cache_key = learn_cache_key(request, response, timeout, settings.CACHE_MIDDLEWARE_KEY_PREFIX, cache=self.cache)               
            if hasattr(response, 'render') and callable(response.render):                                            
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)                                                  
                )
            else:                                                                                                    
                self.cache.set(cache_key, response, timeout)
        return response

class BetterFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        if not request.method in ('GET', 'HEAD'):
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        # try and get the cached GET response
        cache_key = get_cache_key(request, settings.CACHE_MIDDLEWARE_KEY_PREFIX, 'GET', cache=self.cache)
        if cache_key is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.
        response = self.cache.get(cache_key, None)
        # if it wasn't found and we are looking for a HEAD, try looking just for that
        if response is None and request.method == 'HEAD':
            cache_key = get_cache_key(request, self.key_prefix, 'HEAD', cache=self.cache)
            response = self.cache.get(cache_key, None)

        if response is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.
        # hit, return cached response
        request._cache_update_cache = False
        return response

