# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from Interface import Interface

class IXMLProducer(Interface):
    def get_xml():
        """ Returns a stream of XML representative of the object.
        
        """
    