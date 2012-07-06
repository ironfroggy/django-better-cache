from bettercache.utils import CachingMixin, strip_wsgi
from bettercache.proxy import proxy

import logging
logger = logging.getLogger(__name__)

class BetterView(CachingMixin):
    """Accepts any path and attempts to serve it from the cache. If it cannot
    find the response in the cache, it will use ``bettercache.proxy`` to fulfill
    it, and cache the response.
    """

    def get(self, request):
        response = None
        #should this bypass this replicates part of the irule
        if not self.should_bypass_cache(request):
            response, expired = self.get_cache(request)
            # send off the celery task if it's expired
            if expired:
                logger.info("EXPIRED sending task for %s" % request.build_absolute_uri())
                self.send_task(request, response)
            elif response:
                logger.debug("not sending task for %s" % request.build_absolute_uri())
            else:
                logger.info("MISS for: %s" % request.build_absolute_uri())

        # if response is still none we have to proxy
        if response is None:
            logger.debug('PROXY from: %s' % request.build_absolute_uri())
            response = proxy(request)
            response['X-Bettercache-Proxy'] = 'true'
        else:
            response['X-Bettercache-Proxy'] = 'false'
            logger.info('HIT for: %s' % request.build_absolute_uri())

        return response


#TODO: properly implement a class based view
BV = BetterView()
cache_view = BV.get
