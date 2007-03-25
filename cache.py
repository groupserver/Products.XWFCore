from zope.interface.declarations import implements
from zope.interface.interface import Interface
import ThreadLock

class ICache(Interface):
    def set_max_objects(max):
        """ Set the maximum number of objects that the cache may contain.
        
        This may not be implemented by some classes, since not all caches
        may want to implement expiry based on this parameter.
        
        """
        
    def add(key, object):
        """ Add an object to the cache.
        
        """
        
    def has_key(key):
        """ Check to see if an object is in the cache.
        
        """
        
    def get(key):
        """ Get an object from the cache by key.
        
        """

class SimpleCache:
    """ Implement ICache with no expiry.
    
    """
    implements(ICache)
    __thread_lock = ThreadLock.allocate_lock()
    def __init__(self):
        self.cache = {}
        
    def set_max_objects(self, max):
        raise NotImplementedError
        
    def add(self, key, object):
        try:
            self.__thread_lock.acquire()
            self.cache[key] = object
        finally:
            self.__thread_lock.release()
        
        return True
    
    def has_key(self, key):
        return self.cache.has_key(key)
        
    def get(self, key):
        return self.cache.get(key, None)

class LRUCache:
    """ Implements a ICache based on a Least Recently Used mechanism.
    
    """
    implements(ICache)
    __thread_lock = ThreadLock.allocate_lock()
    def __init__(self):
        self.cache = {}
        self.cache_keys = []
        self.set_max_objects(128) # set default
        
    def set_max_objects(self, size):
        self.cache_size = size
        
    def __do_add(self, key, object):
        try:
            self.cache_keys.remove(key)
        except ValueError:
            pass
        
        self.cache[key] = object
        self.cache_keys.insert(0, key)
        
        if len(self.cache_keys) > self.cache_size:
            for key in self.cache_keys[self.cache_size:]:
                del(self.cache[key])
                self.cache_keys = self.cache_keys[:self.cache_size]
                
        return True
    
    def add(self, key, object):
        try:
            self.__thread_lock.acquire()
            return self.__do_add(key, object)
        finally:
            self.__thread_lock.release()
    
    def has_key(self, key):
        return self.cache.has_key(key)
        
    def get(self, key):
        return self.cache.get(key, None)
