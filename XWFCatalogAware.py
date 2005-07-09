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
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
from AccessControl import Role, getSecurityManager, ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from Products.XWFCore.XWFUtils import getToolByName

class XWFCatalogAware(CatalogAware, Role.RoleManager):
    """ Add awareness of the Catalog to the object
    
    """
    security = ClassSecurityInfo()
     
    meta_type = 'XWF Catalog'
     
    # Supplement the security setting management methods to force the
    # security to be reindexed
    def manage_addLocalRoles(self, userid, roles, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_addLocalRoles(self, userid, roles, REQUEST)
        self.reindexObjectSecurity()
        return result
        
    def manage_setLocalRoles(self, userid, roles, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_setLocalRoles(self, userid, roles, REQUEST)
        self.reindexObjectSecurity()
        return result        

    def manage_delLocalRoles(self, userids, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_delLocalRoles(self, userids, REQUEST)
        self.reindexObjectSecurity()
        return result
               
    def manage_delLocalGroupRoles(self, userids, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_delLocalGroupRoles(self, userids, REQUEST)
        self.reindexObjectSecurity()
        return result
        
    def manage_addLocalGroupRoles(self, userids, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_addLocalGroupRoles(self, userids, REQUEST)
        self.reindexObjectSecurity()
        return result

    def manage_delLocalGroupRoles(self, userids, REQUEST=None):
        """ Override of local role management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_delLocalGroupRoles(self, userids, REQUEST)
        self.reindexObjectSecurity()
        return result

    def manage_changePermissions(self, REQUEST):
        """ Override of permission management to provide reindexing.
        
        """
        result = Role.RoleManager.manage_changePermissions(self, REQUEST)
        self.reindexObjectSecurity()
        return result

    security.declareProtected('View', 'reindexObjectSecurity')
    def reindexObjectSecurity(self):
        """
            Reindex security-related indexes on the object
            (and its descendants).
        """
        catalog = getToolByName(self, self.default_catalog)
        path = '/'.join(self.getPhysicalPath())
        for brain in catalog.searchResults(path=path):
            ob = brain.getObject()
            if ob is None:
                # Ignore old references to deleted objects.
                continue
            s = getattr(ob, '_p_changed', 0)
            catalog.reindexObject(ob, idxs=['allowedRolesAndUsers'],
                                  update_metadata=0)
            if s is None: ob._p_deactivate()
        # Reindex the object itself, as the PathIndex only gave us
        # the descendants.
        catalog.reindexObject(self, idxs=['allowedRolesAndUsers'],
                              update_metadata=0)
