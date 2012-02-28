.. Django Bettercache documentation master file, created by
   sphinx-quickstart on Mon Aug  1 10:04:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Bettercache's documentation!
==============================================
Bettercache provides a handful of different caching features. There is a cache templatetag that provides invalidation. There

Template Tag
_____________
The bettercache cache template tag provides some automatic invalidation


Middleware
__________
Bettercache middleware serves as an improved version of the django caching middleware allowing better control of cache headers and easier to generate cache keys.

Celery Task
___________
The bettercache celery task allows most pages to be updated offline in a post check fashion. This means a user never has too wait for a slow page
when serving a cached one would be acceptable.

Proxy Server
____________
The bettercache proxy server can serve pages cached by the bettercache middleware and deal with updating via the celery task.

Cache Backend
_____________
Currently not implemented this will be a django 1.3 compatible caching backend with stampede prevention and check and set support


Contents:

.. toctree::
   :maxdepth: 2

   middleware
   proxy

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

