# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from OFS.SimpleItem import SimpleItem
from Products.ZCatalog.CatalogPathAwareness import CatalogAware

ZopeTestCase.installProduct('XWFCore')
ZopeTestCase.installProduct('ZCatalog')

from Products.XWFCore import XWFMultiplePathIndex

testXML = """<?xml version="1.0" ?>
<root>
  <testnode someattribute="foo">
    Some test text.
  </testnode>
  <emptynode anotherattribute="wibble"/>
</root>"""

class FakePOSTRequest:
    """ A really minimal class to fake a POST. Probably looks
    nothing like the real thing, but close enough for our needs :)
    
    """
    import StringIO
    stdin = StringIO.StringIO(testXML)

class TestClass(SimpleItem, CatalogAware):
    def __init__(self, id):
        self.id = id
    
    multiple_paths_property =  ('one/two/three', 'one/four/five', 'six/seven/eight')

    def multiple_paths_method(self):
        return ('one/two/three', 'one/four/five', 'six/seven/eight')

def minimallyEqualXML(one, two):
    """ Strip all the whitespace out of two pieces of XML code, having first converted
    them to a DOM as a minimal test of equivalence.
    
    """
    from xml.dom import minidom
    
    sf = lambda x: filter(lambda y: y.strip(), x)
    
    onedom = minidom.parseString(one)
    twodom = minidom.parseString(two)
    
    return sf(onedom.toxml()) == sf(twodom.toxml())

from Products.XWFCore.XWFMultiplePathIndex import MultiplePathIndex
class TestXWFMultiplePathIndex(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.folder.manage_addProduct['ZCatalog'].manage_addZCatalog('Catalog',
                                                                                                                   'Catalog')
        self._catalog = self.folder.Catalog._catalog        

    def beforeTearDown(self):
        pass
        
    def _setupCatalog(self, index_name):
        self._catalog.addIndex(index_name, 
                                 XWFMultiplePathIndex.MultiplePathIndex(index_name))
                                 
    def _setupCatalogableObject(self, object_name):
        self.folder._setOb(object_name, TestClass(object_name))
        getattr(self.folder, object_name).index_object()
        
    def _searchCatalog(self, index_name, query, limit=None):
        query_dict = {}
        query_dict['query'] = query
        if limit:
            query_dict['limit'] = limit
        
        return self._catalog.searchResults({index_name: query_dict})

    def _numResults(self, index_name, query, limit=None):
        return len(self._searchCatalog(index_name, query, limit))

    def test_01_createMultiplePathIndexProperty(self):
        self._setupCatalog('multiple_paths_property')
        self._setupCatalogableObject('foo')
        self.assertEqual(self._numResults('mutiple_paths_property', 'one/two'), 1)
                
    def test_02_createMultiplePathIndexMethod(self):
        self._setupCatalog('multiple_paths_method')
        self._setupCatalogableObject('foo')
        self.assertEqual(self._numResults('mutiple_paths_method', 'one/two'), 1)
    
    def test_03_indexLotsOfObjects(self):
        self._setupCatalog('multiple_paths_method')
        for i in xrange(1000):
            self._setupCatalogableObject('foo_%s' % i)
        
        self.assertEqual(self._catalog.getIndex('multiple_paths_method').numObjects(),
                         1000)
        
    def test_04_unindexLotsOfObjects(self):
        self.test_03_indexLotsOfObjects()
        total = 0
        for object in self._searchCatalog('multiple_paths_method', 'one/two'):
            total += 1
            object.getObject().unindex_object()
        
        self.assertEqual(total, 1000)

        self.assertEqual(self._catalog.getIndex('multiple_paths_method').numObjects(),
                         0)

if __name__ == '__main__':
    print framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestXWFMultiplePathIndex))
        return suite
