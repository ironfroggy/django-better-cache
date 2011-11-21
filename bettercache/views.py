import urllib2, time

from django.http import HttpResponse
from bettercache.utils import CachingMixin
from bettercache.tasks import GeneratePage


class BetterView(CachingMixin):
    def get(self, request):
        response = None
        #should this bypass
        if not self.should_bypass_cache(request):
            response, expired = self.get_cache(request)
            # send off the celery task if it's expired
            if expired:
                GeneratePage.apply_async((strip_wsgi(request),))
                self.set_cache(request, response)

        # if response is still none we have to proxy
        if response is None:
            response = self.proxy(request)

        return response #HttpResponse('OH YEAH')

    def proxy(self, request):
        response = urllib2.urlopen('http://www.test.clarkhoward.com',str(time.time))
        hr = HttpResponse(response.read())
        return hr


#TODO: properly implement a class based view
BV = BetterView()
cache_view = BV.get
