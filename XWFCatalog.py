# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# This file also contains code used directly or modified from original Zope
# sources, which are covered by the Zope Public Licence Version 2.0. 
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
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
        result = list( user.getRoles() )
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
