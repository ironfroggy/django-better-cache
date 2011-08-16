from celery.task import Task

from django.core.handlers.base import BaseHandler

class GeneratePage(Task):
    def run(self, request, *args, **kwargs):
        pass
