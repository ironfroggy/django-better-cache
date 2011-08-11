from django.conf import settings
from django.middleware.cache import UpdateCacheMiddleware
from django.utils.cache import patch_response_headers, get_max_age, learn_cache_key

from bettercache.utils import set_post_pre_check_headers

class BetterUpdateCacheMiddleware(UpdateCacheMiddleware):

    def set_headers(self, request, response):
        """ Hook for setting additional headers """
        set_post_pre_check_headers(response)
        response['Edge-control'] = "cache-maxage=1d"

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
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix, cache=self.cache)               
            if hasattr(response, 'render') and callable(response.render):                                            
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)                                                  
                )
            else:                                                                                                    
                self.cache.set(cache_key, response, timeout)
        return response 
