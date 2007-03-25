from zope.interface.declarations import implements
from zope.interface.interface import Interface
import ThreadLock

class ICache(Interface):
    def set_cache_size(size):
        """ Set the maximum size of the cache, in number of items.
        
        """
        
    def add(key, object):
        """ Add an object to the cache.
        
        """
        
    def has_key(self, key):
        """ Check to see if an object is in the cache.
        
        """
        
    def get(key):
        """ Get an object from the cache by key.
        
        """

class SimpleCache:
    implements(ICache)
    __thread_lock = ThreadLock.allocate_lock()
    def __init__( self ):
        self.cache = {}
        
    def set_cache_size(self, size):
        raise UnimplementedError
        
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
    implements(ICache)
    __thread_lock = ThreadLock.allocate_lock()
    def __init__( self ):
        self.cache = {}
        self.cache_keys = []
        self.set_cache_size( 128 ) # default to 128
        
    def set_cache_size(self, size):
        self.cache_size = size
        
    def __do_add(self, key, object):
        try:
            self.cache_keys.remove(key)
        except ValueError:
            pass
        
        self.cache[key] = object
        self.cache_keys.insert(0, key)
        
        if len(self.cache_keys) > self.cache_size:
            for item in self.cache_keys[self.cache_size:]:
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
