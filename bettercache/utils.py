import time
from copy import copy

from django.conf import settings
from django.core.cache import cache
from django.utils.cache import cc_delim_re
from django.utils.encoding import smart_str
from django.utils.http import http_date, parse_http_date

import logging
logger = logging.getLogger()

CACHEABLE_STATUS = [200, 203, 300, 301, 404, 410]

class CachingMixin(object):
    """Common facilities bettercache needs to deal with cache headers."""

    def patch_headers(self, response):
        """Set the headers we want for caching."""

        # Remove Vary:Cookie if we want to cache non-anonymous
        if not getattr(settings, 'BETTERCACHE_ANONYMOUS_ONLY', False):
            vdict = get_header_dict(response, 'Vary')
            try:
                vdict.pop('cookie')
            except KeyError:
                pass 
            else:
                set_header_dict(response, 'Vary', vdict)

        #  Set max-age, post-check and pre-check
        cc_headers = get_header_dict(response, 'Cache-Control')
        try:
            timeout = cc_headers['max-age']
        except KeyError:
            timeout = settings.BETTERCACHE_CACHE_MAXAGE
            cc_headers['max-age'] = timeout
        # This should never happen but let's be safe
        if timeout is 0:
            return response
        if not 'pre-check' in cc_headers:
           cc_headers['pre-check'] = timeout
        if not 'post-check' in cc_headers:
           cc_headers['post-check'] = int(timeout * settings.BETTERCACHE_EDGE_POSTCHECK_RATIO)
        set_header_dict(response, 'Cache-Control', cc_headers)
        # this should be the main/first place we're setting edge control so we can just set what we want
        ec_dict = {'cache-maxage' : settings.BETTERCACHE_EDGE_MAXAGE}
        set_header_dict(response, 'Edge-Control', ec_dict)
        response['Last-Modified'] = http_date()
        return response


    def session_accessed(self, request):
        """from django.middleware.cache.UpdateCacheMiddleware._session_accesed"""

        try:
            return request.session.accessed
        except AttributeError:
            return False

    def should_cache(self, request, response):
        """ Given the request and response should it be cached """

        if not getattr(request, '_cache_update_cache', False):
            return False
        if not response.status_code in getattr(settings, 'BETTERCACHE_CACHEABLE_STATUS', CACHEABLE_STATUS):
            return False
        if getattr(settings, 'BETTERCACHE_ANONYMOUS_ONLY', False) and self.session_accessed and request.user.is_authenticated:
            return False
        if self.has_uncacheable_headers(response):
            return False
        return True

    @staticmethod
    def should_bypass_cache(request):
        """ Should a request not be served from cache """
        
        try:
            if 'no-cache' in request.META['HTTP_CACHE_CONTROL']:
                return True
        except KeyError:
            pass
        return False

    def should_regenerate(self, response):
        """ Check if this page was originally generated less than LOCAL_POSTCHECK seconds ago """
        
        if response.has_header('Last-Modified'):
            last_modified = parse_http_date(response['Last-Modified'])
            next_regen = last_modified + settings.BETTERCACHE_LOCAL_POSTCHECK
            return time.time() > next_regen

    def has_uncacheable_headers(self, response):
        """ Should this response be cached based on it's headers
            broken out from should_cache for flexibility
        """

        cc_dict = get_header_dict(response, 'Cache-Control')
        if cc_dict:
            if cc_dict.has_key('max-age') and cc_dict['max-age'] == '0':
                return True
            if cc_dict.has_key('no-cache'):
                return True
            if cc_dict.has_key('private'):
                return True
        if response.has_header('Expires'):
            if parse_http_date(response['Expires']) < time.time():
                return True
        return False

    def set_cache(self, request, response):
        """ caches the response supresses and logs exceptions"""

        try:
            cache_key = self.cache_key(request)
            #presumably this is to deal with requests with attr functions that won't pickle
            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(lambda r: cache.set(cache_key, (r, time.time(),), settings.BETTERCACHE_LOCAL_MAXAGE))
            else:
                cache.set(cache_key, (response, time.time(),) , settings.BETTERCACHE_LOCAL_MAXAGE)
        except:
            logger.error("failed to cache to %s" %cache_key)

    def get_cache(self, request):
        """ Attempts to get a response from cache, returns a tuple of the response and whether it's expired
            If there is no cached response return (None, None,)
        """

        # try and get the cached GET response
        cache_key = self.cache_key(request)
        cached_response = cache.get(cache_key, None)
        # if it wasn't found and we are looking for a HEAD, try looking for a corresponding GET
        if cached_response is None and request.method == 'HEAD':
            cache_key = self.cache_key(request, 'GET')
            cached_response = cache.get(cache_key, None)
        if cached_response is None:
            return None, None
        if cached_response[1] < time.time() - settings.BETTERCACHE_LOCAL_POSTCHECK:
            return cached_response[0], True
        return cached_response[0], False

    def cache_key(self, request, method=None):
        """ the cache key is the absolute uri and the request method """

        if method is None:
            method = request.method
        return "bettercache_page:%s:%s" %(request.build_absolute_uri(), method)

    def send_task(self, request, response):
        """send off a celery task for the current page and recache"""

        # TODO is this too messy?
        from bettercache.tasks import GeneratePage
        try:
            GeneratePage.apply_async((strip_wsgi(request),))
        except:
            logger.error("failed to send celery task")
        self.set_cache(request, response)


def get_header_dict(response, header):
    """ returns a dictionary of the cache control headers
        the same as is used by django.utils.cache.patch_cache_control 
        if there are no Cache-Control headers returns and empty dict
    """
    def dictitem(s):
        t = s.split('=', 1)
        if len(t) > 1:
            return (t[0].lower(), t[1])
        else:
            return (t[0].lower(), True)

    if response.has_header(header):
        hd = dict([dictitem(el) for el in cc_delim_re.split(response[header])])
    else:
        hd= {}
    return hd

def set_header_dict(response, header, header_dict):
    """Formats and sets a header dict in a response, inververs of get_header_dict."""
    def dictvalue(t):
        if t[1] is True:
            return t[0]
        return t[0] + '=' + smart_str(t[1])

    response[header] = ', '.join([dictvalue(el) for el in header_dict.items()])

def smart_import(mpath):
    """Given a path smart_import will import the module and return the attr reffered to."""
    try:
        rest = __import__(mpath)
    except ImportError:
        split = mpath.split('.')
        rest = smart_import('.'.join(split[:-1]))
        rest = getattr(rest, split[-1])
    return rest

def strip_wsgi(request):
    """Strip WSGI data out of the request META data."""

    meta = copy(request.META)
    for key in meta:
        if key[:4] == 'wsgi':
            meta[key] = None
    return meta
