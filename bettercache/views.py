from bettercache.utils import CachingMixin, strip_wsgi
from bettercache.tasks import GeneratePage
from bettercache.proxy import proxy

import logging
logger = logging.getLogger()

class BetterView(CachingMixin):
    def get(self, request):
        response = None
        #should this bypass this replicates part of the irule
        if not self.should_bypass_cache(request):
            response, expired = self.get_cache(request)
            # send off the celery task if it's expired
            if expired:
                logger.info("sending task for %s" %request.build_absolute_uri)
                self.send_task(request, response)
            else:
                logger.info("sending task for %s" %request.build_absolute_uri)

        # if response is still none we have to proxy
        if response is None:
            logger.info('request %s proxied' %request.build_absolute_uri)
            response = proxy(request)
            #TODO: delete the following two lines
            #self.set_cache(request, response)
            response['X-Bettercache-Proxy'] = 'true'
        else:
            response['X-Bettercache-Proxy'] = 'false'
            logger.info('request %s from cache' %request.build_absolute_uri)

        return response


#TODO: properly implement a class based view
BV = BetterView()
cache_view = BV.get
