from django.conf import settings
from django.core.handlers.base import BaseHandler

from bettercache.utils import smart_import

class AsyncHandler(BaseHandler):
    def __init__(self):
        super(AsyncHandler, self).__init__()

    def load_middleware(self):
        super(AsyncHandler, self).load_middleware()
        # async_middleware = smart_import(settings.ASYNC_MIDDLEWARE)
        # middleware_blacklist = [smart_import(midd) for midd in settings.ASYNC_MIDDLEWARE_BLACKLIST]
        # TODO: pull out the other middleware here
        # TODO: Only pull out of process request except for ourself

    def __call__(self, request):
        self.load_middleware()
        response = self.get_response()
        return response
