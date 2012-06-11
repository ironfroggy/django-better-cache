from django.conf import settings
from django.core.handlers.base import BaseHandler

class AsyncHandler(BaseHandler):
    """Used to process HTTP requests from celery tasks."""

    def __init__(self):
        super(AsyncHandler, self).__init__()

    def load_middleware(self):
        # is there a better way to do this than putting it here?
        # from bettercache.middleware import BetterCacheMiddleware
        super(AsyncHandler, self).load_middleware()
        # self._request_middleware = [m for m in self._request_middleware if not issubclass(m, BetterCacheMiddleware)]
        # self._response_middleware = [m for m in self._response_middleware if not issubclass(m, BetterCacheMiddleware)]
        # middleware_blacklist = [smart_import(midd) for midd in settings.ASYNC_MIDDLEWARE_BLACKLIST]

    def __call__(self, request):
        self.load_middleware()
        response = self.get_response(request)
        return response
