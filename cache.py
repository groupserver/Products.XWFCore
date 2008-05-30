#
# This code has test cases in tests/test_cache.py.
# Modifications without a supporting test case will be rejected.
#

from zope.interface.declarations import implements
from zope.interface.interface import Interface
import datetime

from threading import Lock

import logging
log = logging.getLogger('XWFCore.cache')

class ICache(Interface):
    def set_max_objects(max):
        """ Set the maximum number of objects that the cache may contain.
        
        This may not be implemented by some classes, since not all caches
        may want to implement expiry based on this parameter.
        
        """

    def set_expiry_interval(self, dt):
        """ Set the expiry interval of the cache, passing in a datetime.timedelta
        object.

        This may not be implemented by some classes, since not all classes
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

    def remove(key):
        """ Remove an object from the cache by key.

        """
        
    def clear():
        """Clear all instances from a cache
        """

class SimpleCache:
    """ Implement ICache with no expiry.
    
    """
    implements(ICache)
    __thread_lock = Lock()
    def __init__(self):
        self.cache = {}
        
    def set_max_objects(self, max):
        raise NotImplementedError

    def set_expiry_interval(self, dt):
        raise NotImplementedError
        
    def add(self, key, object):
        try:
            if not self.__thread_lock.acquire(False):
                log.info("Not adding object to cache, would have required blocking")
                return False
            
            self.cache[key] = object
        finally:
            try:
                self.__thread_lock.release()
            except:
                pass
        
        return True
    
    def has_key(self, key):
        return self.cache.has_key(key)
        
    def get(self, key):
        return self.cache.get(key, None)

    def remove(self, key):
        try:
            del(self.cache[key])
        except KeyError, e:
            pass
            
    def clear(self):
        self.cache = {}

class SimpleCacheWithExpiry:
    """ Implement ICache with expiry.
    
    """
    implements(ICache)
    __thread_lock = Lock()
    def __init__(self):
        self.cache = {}
        self.expiry_interval = None
                
    def set_max_objects(self, max):
        raise NotImplementedError

    def set_expiry_interval(self, dt):
        if not isinstance(dt, datetime.timedelta):
            raise TypeError('expiry interval must be an instance of datetime.timedelta')
        
        self.expiry_interval = dt
        
    def add(self, key, object):
        try:
            if not self.__thread_lock.acquire(False):
                log.info("Not adding object to cache, would have required blocking")
                return False
            self.cache[key] = (datetime.datetime.now()+self.expiry_interval,
                               object)
        finally:
            try:
                self.__thread_lock.release()
            except:
                pass
        
        return True
    
    def has_key(self, key):
        return self.cache.has_key(key)
        
    def get(self, key):
        cache_object = self.cache.get(key, None)
        retval = None
        if cache_object and datetime.datetime.now() < cache_object[0]:
            retval = cache_object[1]
        elif cache_object:
            del(self.cache[key])
            
        return retval

    def remove(self, key):
        try:
            del(self.cache[key])
        except KeyError, e:
            pass

    def clear(self):
        self.cache = {}        

class LRUCache:
    """ Implements a ICache based on a Least Recently Used mechanism.
    
    """
    implements(ICache)
    __thread_lock = Lock()
    def __init__(self):
        self.cache = {}
        self.cache_keys = []
        self.set_max_objects(128) # set default
        
    def set_max_objects(self, size):
        self.cache_size = size

    def set_expiry_interval(self, dt):
        raise NotImplementedError
        
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
            if not self.__thread_lock.acquire(False):
                log.info("Not adding object to cache, would have required blocking")
                return False
            return self.__do_add(key, object)
        finally:
            try:
                self.__thread_lock.release()
            except:
                pass
    
    def has_key(self, key):
        return self.cache.has_key(key)
        
    def get(self, key):
        return self.cache.get(key, None)

    def remove(self, key):
        try:
            del(self.cache[key])
        except KeyError, e:
            pass

    def clear(self):
        self.cache = {}
        self.cache_keys = []

