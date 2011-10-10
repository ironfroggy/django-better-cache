from celery.task import Task

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db import connections
from bettercache.handlers import AsyncHandler
from bettercache.utils import CachingMixin

import logging
logger = logging.getLogger()

class GeneratePage(Task, CachingMixin):
    """ GeneratePage takes a request and generates a response which it sticks in the cache if appropriate """
    queue = 'pagegen'


    def run(self, meta, *args, **kwargs):
        # TODO: subclass WSGIRequest so all of the wsgi stuff is actually gone
        request = WSGIRequest(meta)
        request._cache_update_cache = True
        if not self.should_rebuild(request):
            return
        handler = AsyncHandler()
        response = handler(request)
        # TODO: this is medley specific and horrific get rid of it
        self.set_db('write_master')
        if self.should_cache(request, response):
            self.patch_headers(response)
            self.set_cache(request, response)
        elif response.status_code == 500:
            logger.error('Failed to generate page %s' %request.path)
        return response

    def should_rebuild(self, request):
        """ If the page in cache is recent don't bother rebuilding it """
        return True

    def set_db(self, dbname):
        db = settings.DATABASES[dbname]
        settings.DATABASES['default'] = db
        try:
            conn = connections['default']
            conn.close()
            connections._connections.pop('default')
        except KeyError:
            pass
