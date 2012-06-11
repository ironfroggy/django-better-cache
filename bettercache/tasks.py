from celery.task import Task

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db import connections
from bettercache.handlers import AsyncHandler
from bettercache.utils import CachingMixin

import logging
logger = logging.getLogger()

class GeneratePage(Task, CachingMixin):
    """ GeneratePage takes a request and generates a response which it sticks
    in the cache if appropriate.
    
    Updating cached responses via celery allows a caching server or
    middleware to serve up an existing cache entry, and then ensure it gets
    updated with a new copy without waiting for the new copy before handing
    a response back for the current request. This keeps the cache up to date,
    and the response times minimal. Cache expirations don't imply a hidden
    danger of latency.
    """
    
    queue = 'pagegen'
    ignore_result = True

    def run(self, meta, *args, **kwargs):
        # TODO: subclass WSGIRequest so all of the wsgi stuff is actually gone
        request = WSGIRequest(meta)
        request._cache_update_cache = True
        if not self.should_rebuild(request):
            return
        handler = AsyncHandler()
        response = handler(request)

    def set_db(self, dbname):
        db = settings.DATABASES[dbname]
        settings.DATABASES['default'] = db
        try:
            conn = connections['default']
            conn.close()
            connections._connections.pop('default')
        except KeyError:
            pass
