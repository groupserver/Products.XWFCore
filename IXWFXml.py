# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from Interface import Interface

class IXmlProducer(Interface):
    def get_xml():
        """ Returns a stream of XML representative of the object.
        
        """
        
    def get_xmlMetadataElements(default_ns=''):
        """ Returns a stream of XML representative of the metadata of the
        object.
        
        For example, if the object contains metadata attributes 'dc:Title',
        'dc:Description' and 'id', and the default_ns passed is 'foo',
        the metadata stream would be:
        
        <dc:Title>Some title</dc:Title>
        <dc:Description>Some description</dc:Description>
        <foo:id>ObjectID</foo:id>
        
        """
    