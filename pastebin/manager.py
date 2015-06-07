from django.db import models
from django.core.cache import cache

class CachedManager(models.Manager):
    """
    A custom manager that implements simple caching that is used when fetching single entries
    """
    # Key that will be used for caching
    # Eg. with ["char_id", "id"] the model will be saved and retrieved from cache but only
    # if the get() method is given a single char_id OR id argument
    cache_keys = []
    cache_name = None
    
    def get(self, *args, **kwargs):
        """
        If only one argument is passed and it's in cache_keys, the result
        will be attempted to be pulled from cache
        """
        if len(kwargs) == 1 and kwargs[kwargs.keys()[0]] in self.cache_keys:
            cache_key = kwargs[kwargs.keys()[0]]
            result = cache.get("%s:%s" % (self.cache_name, cached_key))
            
            if result != None:
                return result
            
        result = super(CachedManager, self).get(*args, **kwargs)
        
        for cache_key in cache_keys:
            cache.set("%s:%s" % (self.cache_name, cache_key), result)
            
        return result