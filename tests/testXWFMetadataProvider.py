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

from Products.XWFCore.XWFMetadataProvider import XWFMetadataProvider
from Products.XWFCore.IXWFMetadataProvider import IXWFMetadataProvider

class TestXWFMultiplePathIndex(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.metadataProvider = XWFMetadataProvider()        

    def beforeTearDown(self):
        pass
    
    def _setupSomeNamespaces(self, setup_default=0):
        for ns, ns_prefix in (('http://xwft.org/ns/foo', 'foo'),
                              ('http://xwft.org/ns/wibble', 'wibble'),
                              ('http://xwft.org/ns/blarg', 'blarg')):
            self.metadataProvider.set_metadataNS(ns, ns_prefix)
        if setup_default:
            self.metadataProvider.set_metadataNSDefault('http://xwft.org/ns/default')
        return 1
    
    def _setupMetadataIndexes(self):
        for metadata_id, ns, index_type in (('Title', 'foo', 'KeywordIndex'),
                                ('Description', 'foo', 'TextIndex'),
                                ('Title', 'wibble', 'KeywordIndex'),
                                ('Description', 'wibble', 'TextIndex'),
                                ('Title', '', 'KeywordIndex'),
                                ('Description', '', 'TextIndex')):
            self.metadataProvider.set_metadataIndex(metadata_id, ns, index_type)
    
    def test_01_createMetadataProvider(self):
        # simply test that the setup correctly created the metadata provider
        self.failUnless(isinstance(self.metadataProvider, XWFMetadataProvider))        
        self.assertEqual(
            IXWFMetadataProvider.isImplementedBy(self.metadataProvider), 1)
        
    def test_02_setMetadataNS(self):
        self._setupSomeNamespaces()
        self.assertEqual(self.metadataProvider.get_metadataNSPrefix('http://xwft.org/ns/foo'),
                         'foo')
        self.assertEqual(self.metadataProvider.get_metadataNSPrefix('http://xwft.org/ns/wibble'),
                         'wibble')
        self.failUnless(not self.metadataProvider.get_metadataNSDefault())
    
    def test_03_setDefaultMetadataNS(self):
        self._setupSomeNamespaces(1)
        self.assertEqual(self.metadataProvider.get_metadataNSDefault(),
                         'http://xwft.org/ns/default')              
        self.assertEqual(self.metadataProvider.get_metadataNSPrefix('http://xwft.org/ns/default'),
                         '')
        self.assertEqual(self.metadataProvider.get_metadataNSPrefix('http://xwft.org/ns/nonexistent'),
                         None)
                         
    def test_04_setMetadataIndex(self):
        self._setupSomeNamespaces(1)
        self._setupMetadataIndexes()
        self.assertEqual(self.metadataProvider.get_metadataIndex('Title'),
                         'KeywordIndex')
        self.assertEqual(self.metadataProvider.get_metadataIndex('Description', 'wibble'),
                         'TextIndex')
    
    def test_05_removeMetadataIndex(self):
        self._setupSomeNamespaces(1)
        self._setupMetadataIndexes()
        self.assertEqual(self.metadataProvider.remove_metadataIndex('Title'), 1)
        self.assertEqual(self.metadataProvider.remove_metadataIndex('Title'), 0)
        self.assertEqual(self.metadataProvider.get_metadataNSPrefixMap(''),
                         {'Description': 'TextIndex'})
        self.assertEqual(self.metadataProvider.remove_metadataIndex('Description'), 1)
        self.assertEqual(self.metadataProvider.get_metadataNSPrefixMap(''),
                         {})

    def test_06_updateMetadataIndex(self):
        self._setupSomeNamespaces(1)
        self._setupMetadataIndexes()
        get_metadataNSPrefixMap = self.metadataProvider.get_metadataNSPrefixMap
        self.assertEqual(get_metadataNSPrefixMap('foo').get('Title'),
                        'KeywordIndex')
        self.assertEqual(get_metadataNSPrefixMap('blarg'), {})
        self.assertEqual(
          self.metadataProvider.update_metadataNS('http://xwft.org/ns/foo',
                                                  'blarg'), 1)
        self.assertEqual(get_metadataNSPrefixMap('foo'), {}) 
        self.assertEqual(get_metadataNSPrefixMap('blarg').get('Title'),
                         'KeywordIndex')

if __name__ == '__main__':
    print framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestXWFMultiplePathIndex))
        return suite
