.. Django Better Cache documentation master file, created by
   sphinx-quickstart on Mon Dec 12 23:03:03 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to Django Better Cache's documentation!
===============================================

Better Cache originally provided a replacement ``{% cache %}`` tag, but as of
version 0.6 includes a Cache ORM module and a suite of caching and proxy tools.
Overall, the aim is to simplify and empower your use of caches with sane
defaults and obvious behaviors.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   templatetags
   cachemodel
   middleware
   proxy
   api
   roadmap


Template Tag
_____________
The bettercache :doc:`cache template tag </templatetags>` provides some automatic invalidation. 

Cache ORM
_________
Caching can be more than a string and random object. ``bettercache.objects`` provides an ORM interface to structure caching and manage keys for you, replacing a mix-mash of adhoc key generation and fragile object pickling with stabl cache models and key management.

Middleware
__________
Bettercache :ref:`middleware <intro-to-middleware>` serves as an improved version of the django caching middleware allowing better control of cache headers and easier to generate cache keys.

Celery Task
___________
The bettercache :doc:`celery task </middleware>` allows most pages to be updated offline in a post check fashion. This means a user never has too wait for a slow page
when serving a cached one would be acceptable.

Proxy Server
____________
The bettercache proxy server can serve pages cached by the bettercache middleware and deal with updating via the celery task.

Cache Backend
_____________
Currently not implemented this will be a django 1.3 compatible caching backend with stampede prevention and check and set support

Discussion
----------

You can make suggestions and seek assistance on the mailing list:

https://groups.google.com/forum/#!forum/bettercache


Contributing
------------

Fork and send pull requests, please!

http://github.com/ironfroggy/django-better-cache/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

