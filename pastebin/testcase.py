from django.test import TestCase

from django.core.cache import cache

from django_redis import get_redis_connection

class CacheAwareTestCase(TestCase):
    """
    Cache-aware TestCase that clears both Redis servers on startup
    """
    def setUp(self):
        super(CacheAwareTestCase, self).setUp()
        
        cache.clear()
        con = get_redis_connection("persistent")
        
        con.flushall()