# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
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
