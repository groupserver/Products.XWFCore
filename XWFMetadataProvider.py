# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from IXWFMetadataProvider import IXWFMetadataProvider

class XWFMetadataProvider:
    __implements__ = (IXWFMetadataProvider,)
    
    _metadata_prefix_ns = {} # maps ns_prefix: ns
    _metadata_ns_prefix = {} # maps ns: ns_prefix
    _metadata_index = {} # maps metadata: index_type
    _metadata_prefix_metadata = {} # maps ns_prefix: metadata

    def get_metadataNSPrefix(self, ns):
        """ Return the prefix for namespace requested.
        
            Note that the default namespace will be returned as a prefix
            of '' not None.
        
        """
        return self._metadata_ns_prefix.get(ns, None)
        
    def get_metadataNSPrefixMap(self):
        """ Return a dictionary of all known metadata namespace -> prefix
        mappings.
        
        """
        return self._metadata_ns_prefix
        
    def get_metadataPrefixNSMap(self):
        """ Return a dictionary of all known metadata prefix -> namespace
        mappings.
        
        """
        return self._metadata_prefix_ns
        
    def set_metadataNSDefault(self, ns):
        """ Set the default metadata namespace.
        
            This is functionally equivalent to set_metadataNS('someuri', '').
            
        """
        self._metadata_prefix_ns[''] = ns
        self._metadata_ns_prefix[ns] = ''
        
        self._p_changed = 1

        return 1

    def get_metadataNSDefault(self):
        """ Get the default metadata namespace.
        
        """
        return self._metadata_prefix_ns.get('', None)

    def set_metadataNS(self, ns, ns_prefix):
        """ Set a metadata namespace.
        
        """
        self._metadata_prefix_ns[ns_prefix] = ns
        self._metadata_ns_prefix[ns] = ns_prefix

        self._p_changed = 1
        
        return 1

    def remove_metadataNS(self, ns):
        """ Remove a metadata namespace.
        
        """
        if self._metadata_ns_prefix.has_key(ns):
            ns_prefix = self._metadata_ns_prefix[ns]
            del(self._metadata_ns_prefix[ns])
            del(self._metadata_prefix_ns[ns_prefix])
            if self._metadata_prefix_metadata.has_key(ns_prefix):
                for metadata in self._metadata_prefix_metadata[ns_prefix]:
                    try:
                        del(self._metadata_index[metadata])
                    except KeyError:
                        pass
                del(self._metadata_prefix_metadata[ns_prefix])
                
            return 1
        return 0
    
    def update_metadataNS(self, ns, ns_prefix):
        """ Update a metadata namespace, and all related mappings.
        
        """
        import copy
        
        old_ns_prefix = self.get_metadataNSPrefix(ns)
        self.set_metadataNS(ns, ns_prefix)
        # the ns_prefix can be '', which would be the default ns
        if old_ns_prefix != None:
            m_ids = self._metadata_prefix_metadata.get(old_ns_prefix, [])
            for m_id in copy.copy(m_ids):
                index_type = self.get_metadataIndex(m_id, old_ns_prefix)
                self.remove_metadataIndex(m_id, old_ns_prefix)
                self.set_metadataIndex(m_id, ns_prefix, index_type)
                
        return 1
                
    def _genCanonicalMetadataId(self, metadata_id, ns_prefix=''):
        if ns_prefix:
            canonical_metadata = '%s:%s' % (ns_prefix, metadata_id)
        else:
            canonical_metadata = metadata_id
            
        return canonical_metadata

    def set_metadataIndex(self, metadata_id, ns_prefix='', index_type=None):
        """ Define a new kind of metadata.
        
        """
        canonical_metadata = self._genCanonicalMetadataId(metadata_id, ns_prefix)
            
        self._metadata_index[canonical_metadata] = index_type
        if (self._metadata_prefix_metadata.has_key(ns_prefix) and
            metadata_id not in self._metadata_prefix_metadata[ns_prefix]):
            self._metadata_prefix_metadata[ns_prefix].append(metadata_id)
        else:
            self._metadata_prefix_metadata[ns_prefix] = [metadata_id]
            
        self._p_changed = 1
        
        return 1
    
    def get_metadataNSPrefixMap(self, ns_prefix):
        """ Returns a dictionary of metadata for a particular NS.
            
            Note: the namespace prefix is stripped.
        """
        metadata = {}
        
        for metadata_id in self._metadata_prefix_metadata.get(ns_prefix, []):
            cm_id = self._genCanonicalMetadataId(metadata_id, ns_prefix)
            if self._metadata_index.has_key(cm_id):
                metadata[metadata_id] = self._metadata_index.get(cm_id)
        
        return metadata
        
    def get_metadataFullNSPrefixMap(self):
        """ Returns a dictionary of all the namespace prefixes along with their
        associated metadata.
        
        """
        return self._metadata_prefix_metadata

    def get_metadataIndex(self, metadata_id, ns_prefix=''):
        """ Returns the index type for a given metadata ID and namespace
        prefix.
        
        """
        canonical_metadata = self._genCanonicalMetadataId(metadata_id, ns_prefix)
        
        return self._metadata_index.get(canonical_metadata, None)

    def get_metadataIndexesMap(self):
        """ Returns a dictionary of all metadata along with their index types.
        
        """
        return self._metadata_index
        
    def remove_metadataIndex(self, metadata_id, ns_prefix=''):
        """ Undefine a kind of metadata.
        
        """
        canonical_metadata = self._genCanonicalMetadataId(metadata_id, ns_prefix)
        
        # remove the metadata from the metadata -> index mapping
        try:
            del(self._metadata_index[canonical_metadata])
        except KeyError:
            return 0
        
        # and remove it from the prefix -> metadata mapping
        try:
            self._metadata_prefix_metadata[ns_prefix].remove(metadata_id)
            # be extra tidy
            if not (self._metadata_prefix_metadata[ns_prefix]):
                del(self._metadata_prefix_metadata[ns_prefix])
        except (KeyError, ValueError):
            return 0
            
        self._p_changed = 1

        return 1
        