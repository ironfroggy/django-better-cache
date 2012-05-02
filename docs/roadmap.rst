Roadmap
=======

0.6
---

The next release of ``bettercache`` is planned to expand upon
the :ref:`CacheModel` even further, handling cache misses and
allow push updates of cached data, among other new treats.

* from_model_APP_MODEL() methods on CacheModel can be implemented to
  update the cached data when models are updated

Future
------

* Secondary key-sets, to allow more than one lookup for the same cache data
* Included Celery tasks to async update the cached data
* Two part from_miss with a sync step that defers the second step to Celery
* Implemented nested invalidation of CacheModels
* Convert the replacement ``{% cache %}`` tag to generate CacheModels
* Add a ``{% notcached %}`` tag to nest inside ``{% cache %}`` blocks
* Add an ``{% else %}`` clause to cache blocks
* Defer rendering of cache blocks to celery
* Push deferred-rendered cache blocks back to pages
