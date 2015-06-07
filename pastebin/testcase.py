from django.test import TestCase

from django.core.cache import cache

from django_redis import get_redis_connection

class CacheAwareTestCase(TestCase):
    """
    Cache-aware TestCase that clears the Redis storage and cache on startup
    """
    def clearCache(self):
        """
        Clears the cache
        
        Can be invoked manually if the unit test requires it
        """
        cache.clear()
        con = get_redis_connection("persistent")
        
        con.flushall()
        
    def setUp(self):
        super(CacheAwareTestCase, self).setUp()
        
        self.clearCache()