from django.conf import settings
from django.utils.cache import cc_delim_re, patch_cache_control, get_max_age

def get_cc_dict(response):
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

    if response.has_header('Cache-Control'):
        cc = dict([dictitem(el) for el in cc_delim_re.split(response['Cache-Control'])])
    else:
        cc= {}
    return cc

def set_post_pre_check_headers(response):
    """ Set the post_check and pre_check headers if not set based on settings and max_age """
    max_age = get_max_age(response)
    if max_age:
        cc_headers = get_cc_dict(response)
        new_headers = {}
        if not 'pre-check' in cc_headers:
           new_headers['pre-check'] = max_age
        if not 'post-check' in cc_headers:
           new_headers['post-check'] = int(max_age * settings.CACHE_POST_CHECK_RATIO)
        if new_headers:
            patch_cache_control(response, **new_headers)
