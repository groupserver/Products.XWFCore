# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from Interface import Interface

class IXWFMetadataProvider(Interface):
    def get_metadataNSPrefix(ns):
        """ Return the prefix for namespace requested.
        
            Note that the default namespace will be returned as a prefix
            of '' not None.
        
        """
        
    def get_metadataNSPrefixMap():
        """ Return a dictionary of all known metadata namespace -> prefix
        mappings.
        
        """
        
    def get_metadataPrefixNSMap():
        """ Return a dictionary of all known metadata prefix -> namespace
        mappings.
        
        """
        
    def set_metadataNSDefault(ns):
        """ Set the default metadata namespace.
        
            This is functionally equivalent to set_metadataNS('someuri', '').
            
        """

    def get_metadataNSDefault():
        """ Get the default metadata namespace.
        
        """

    def set_metadataNS(ns, ns_prefix):
        """ Set a metadata namespace.
        
        """

    def remove_metadataNS(ns):
        """ Remove a metadata namespace.
        
        """
    
    def update_metadataNS(ns, ns_prefix):
        """ Update a metadata namespace, and all related mappings.
        
        """

    def set_metadataIndex(metadata_id, ns_prefix='', index_type=None):
        """ Define a new kind of metadata.
        
        """
        
    def get_metadataNSPrefixMap(ns_prefix):
        """ Returns a dictionary of metadata for a particular NS.
            
            Note: the namespace prefix is stripped.
        """
        
    def get_metadataFullNSPrefixMap():
        """ Returns a dictionary of all the namespace prefixes along with their
        associated metadata.
        
        """

    def get_metadataIndex(metadata_id, ns_prefix=''):
        """ Returns the index type for a given metadata ID and namespace
        prefix.
        
        """

    def get_metadataIndexMap():
        """ Returns a dictionary of all metadata along with their index types.
        
        """
        
    def remove_metadataIndex(metadata_id, ns_prefix=''):
        """ Undefine a kind of metadata.
        
        """
