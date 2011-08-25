from celery.task import Task

from django.core.handlers.wsgi import WSGIRequest
from bettercache.handlers import AsyncHandler
from bettercache.utils import CachingMixin


class GeneratePage(Task, CachingMixin):
    """ GeneratePage takes a request and generates a response which it sticks in the cache if appropriate """
    queue = 'pagegen'


    def run(self, meta, *args, **kwargs):
        request = WSGIRequest(meta)
        if not self.should_rebuild(request):
            return
        handler = AsyncHandler()
        response = handler(request)
        if self.should_cache(request, response):
            self.patch_headers(response)
            self.set_cache(request, response)
        return response

    def should_rebuild(self, request):
        """ If the page in cache is recent don't bother rebuilding it """
        return True
