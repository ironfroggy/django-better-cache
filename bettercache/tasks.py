from celery.task import Task

from bettercache.handlers import AsyncHandler
from bettercache.utils import CachingMixin

class GeneratePage(Task, CachingMixin):

    def run(self, request, *args, **kwargs):
        if self.should_rebuild(request):
            return
        handler = AsyncHandler()
        response = handler.get_response(request)
        if self.should_cache(request, response):
            self.patch_headers(response)
            self.set_cache(request, response)

    def should_rebuild(self, request):
        """ If the page in cache is recent don't bother rebuilding it """
        return True
