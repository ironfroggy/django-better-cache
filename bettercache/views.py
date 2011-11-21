from bettercache.utils import CachingMixin


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

        return response
