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

ZopeTestCase.installProduct('XWFCore')

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
        pass        

    def beforeTearDown(self):
        pass
        
    def test_1_createMultiplePathIndex(self):
        pass
        
if __name__ == '__main__':
    print framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSomeProduct))
        return suite
