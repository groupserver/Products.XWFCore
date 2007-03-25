# coding=utf-8
##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Size adapters for testing

$Id: test_size.py 61072 2005-10-31 17:43:51Z philikon $
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_cache():
    """
    Test cache

    Set up:
      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> from Products.XWFCore import cache

      >>> simple_cache = cache.SimpleCache()
      >>> try:
      ...     simple_cache.set_max_objects(10)
      ... except NotImplementedError:
      ...     pass # this is expected
    
      >>> for i in range(10):
      ...    r = simple_cache.add(str(i), i)
      
      >>> len(simple_cache.cache)
      10
      
      >>> simple_cache.add(str(11), 11)
      True
      
      >>> len(simple_cache.cache)
      11
      
      >>> simple_cache.get(str(11))
      11
      
      >>> simple_cache.has_key(str(5))
      True
      
      >>> simple_cache.has_key(str(12))
      False
      
    The first object in the cache should still be there:
    
      >>> simple_cache.get(str(0)) == 0
      True
    
    Setup a Least Recently Used Cache:
      
      >>> lru_cache = cache.LRUCache()
      >>> lru_cache.set_max_objects(10)
      >>> for i in range(10):
      ...    r = lru_cache.add(str(i), i)
      
      >>> len(lru_cache.cache)
      10
      
      >>> lru_cache.add(str(11), 11)
      True
      
      >>> len(lru_cache.cache)
      10
      
      >>> lru_cache.get(str(11))
      11
      
    The first object in the cache should now have expired:
    
      >>> lru_cache.get(str(0)) == None
      True
    
      >>> lru_cache.has_key(str(0))
      False
    
    The second object in the cache should still be there:
      
      >>> lru_cache.get(str(1)) == 1
      True
      
    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
