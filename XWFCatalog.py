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
from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from AccessControl import getSecurityManager
from Products.ZCatalog.ZCatalog import ZCatalog
from Acquisition import aq_base

from types import StringType

class XWFCatalog(ZCatalog):
    """ A ZCatalog that adds additional filters to queries, primarily
    to remove objects the user doesn't have permission to view.
    
    """
    id = 'xwf catalog'
    meta_type = 'XWF Catalog'
    
    def __init__(self):
        ZCatalog.__init__(self, self.getId())
        self.addIndex('allowedRolesAndUsers', 'KeywordIndex')
        
    def catalog_object(self, object, uid=None, idxs=[]):         
        # Wraps the object with workflow and accessibility
        # information just before cataloging.
        vars = {}
        w = IndexableObjectWrapper(vars, object)
        ZCatalog.catalog_object(self, w, uid, idxs)

    def _listAllowedRolesAndUsers( self, user ):
        result = list( user.getRolesInContext(self) )
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        return result

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        """ Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
            
        """
        user = getSecurityManager().getUser()
        
        # we replace, rather than append the 'allowedRolesAndUsers' index,
        # anything else would be a really big security loophole
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )
        return apply(ZCatalog.searchResults, (self, REQUEST), kw)
 
    __call__ = searchResults
