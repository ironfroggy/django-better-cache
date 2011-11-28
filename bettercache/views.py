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
        url = request.build_absolute_uri()
        #TODO: Don't do this
        url = url.replace('local.www', 'www.test').replace(':8000','')
        print url
        response = urllib2.urlopen(url)
        hr = HttpResponse(response.read())
        return hr

    def get_url(self, request):
        print request.build_absolute_uri()
        import pdb; pdb.set_trace()
        return ''



#TODO: properly implement a class based view
BV = BetterView()
cache_view = BV.get
