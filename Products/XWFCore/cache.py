#
# This code has test cases in tests/test_cache.py.
# Modifications without a supporting test case will be rejected.
#

from zope.interface.declarations import implements
from zope.interface import Interface
import datetime

from threading import RLock

import logging
log = logging.getLogger('XWFCore.cache')

class Caches:
    caches = {}
    __thread_lock = RLock()
    
    def add(self, cache_instance):
        try:
            self.__thread_lock.acquire()
            self.caches[cache_instance.cache_name] = cache_instance
        finally:
            self.__thread_lock.release()
    
    def remove(self, cache_instance):
        try:
            self.__thread_lock.acquire()
            del self.caches[cache_instance.cache_name]
        finally:
            self.__thread_lock.release()

    def has_key(self, cache_name):
        try:
            self.__thread_lock.acquire()
            return self.caches.has_key(cache_name)
        finally:
            self.__thread_lock.release()

    def get(self, cache_name):
        try:
            self.__thread_lock.acquire()
            return self.caches[cache_name]
        finally:
            self.__thread_lock.release()

caches = Caches()

class ICache(Interface):
    def set_max_objects(max): #@NoSelf
        """ Set the maximum number of objects that the cache may contain.
        
        This may not be implemented by some classes, since not all caches
        may want to implement expiry based on this parameter.
        
        """

    def set_expiry_interval(dt): #@NoSelf
        """ Set the expiry interval of the cache, passing in a datetime.timedelta
        object.

        This may not be implemented by some classes, since not all classes
        may want to implement expiry based on this parameter.
        
        """
        
    def add(key, object): #@NoSelf
        """ Add an object to the cache.
        
        """
        
    def has_key(key): #@NoSelf
        """ Check to see if an object is in the cache.
        
        """
        
    def get(key): #@NoSelf
        """ Get an object from the cache by key.
        
        """

    def remove(key): #@NoSelf
        """ Remove an object from the cache by key.

        """
        
    def clear(): #@NoSelf
        """Clear all instances from a cache
        """

def simplecache(cachename, cachekeyfunc):
    def cache_decorator(f):
        def do_cache(*args):
            if caches.has_key(cachename):
                c = caches.get(cachename)
            else:
                c = SimpleCache(cachename)
                caches.add(c)
            cache_key = cachekeyfunc(*args)
            result = c.get(cache_key)
            if not result:
                print 'cache miss'
                result = f(*args)
                c.add(cache_key, result)
            print 'cache hit'
            return result # do_cache

        return do_cache # cache_decorator

    return cache_decorator # simplecache

class SimpleCache:
    """ Implement ICache with no expiry.
    
    """
    implements(ICache)
    __thread_lock = RLock()
    def __init__(self, cache_name=''):
        self.cache = {}
        self.cache_name = cache_name
        
    def set_max_objects(self, max):
        raise NotImplementedError

    def set_expiry_interval(self, dt):
        raise NotImplementedError
        
    def add(self, key, object):
        try:
            if not self.__thread_lock.acquire(False):
                log.info("Cache (%s), not adding object (%s) to cache, would have required blocking" % (self.cache_name, key))
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
    __thread_lock = RLock()
    def __init__(self, cache_name=''):
        self.cache = {}
        self.expiry_interval = None
        self.cache_name = cache_name
                
    def set_max_objects(self, max):
        raise NotImplementedError

    def set_expiry_interval(self, dt):
        if not isinstance(dt, datetime.timedelta):
            raise TypeError('expiry interval must be an instance of datetime.timedelta')
        
        self.expiry_interval = dt
        
    def add(self, key, object):
        try:
            if not self.__thread_lock.acquire(False):
                log.info("Cache (%s), not adding object (%s) to cache, would have required blocking" % (self.cache_name, key))
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
    __thread_lock = RLock()
    def __init__(self, cache_name=''):
        self.cache = {}
        self.cache_keys = []
        self.set_max_objects(128) # set default
        self.cache_name = cache_name        

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
                log.info("Cache (%s), not adding object (%s) to cache, would have required blocking" % (self.cache_name, key))
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

