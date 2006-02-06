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
from types import StringType

from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog
from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import logging
logger = logging.getLogger()

class Record:
    pass

class XWFIndexableObjectWrapper:
    # Primarily borrowed from CMFCore
    def __init__(self, vars, ob):
        self.__vars = vars
        self.__ob = ob

    def __getattr__(self, name):
        vars = self.__vars
        if vars.has_key(name):
            return vars[name]
        return getattr(self.__ob, name)

    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self.__ob
        return self.acl_users._allowedRolesAndUsers(ob)

        allowed = {}
        for r in rolesForPermissionOn(View, ob):
            allowed[r] = 1
        localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        return list(allowed.keys())


class XWFCatalog(ZCatalog):
    """ A ZCatalog that adds additional filters to queries, primarily
    to remove objects the user doesn't have permission to view.
    
    """
    security = ClassSecurityInfo()
    
    meta_type = 'XWF Catalog'
    
    def __init__(self, id='Catalog'):
        ZCatalog.__init__(self, self.getId())
        
        self.addIndex('allowedRolesAndUsers', 'KeywordIndex')
        
    def __url(self, ob):
        return '/'.join(ob.getPhysicalPath())

    def catalog_object(self, object, uid=None, idxs=[], update_metadata=1):         
        vars = {}
        w = XWFIndexableObjectWrapper(vars, object)
        ZCatalog.catalog_object(self, w, uid, idxs, update_metadata)

    def _listAllowedRolesAndUsers(self, user):
        result = list(user.getRoles())
        if not result:
            result.append('Anonymous')
        else:
            result.append('user:%s' % user.getUserName())
        # deal with groups
        getGroups = getattr(user, 'getGroups', None)
        if getGroups is not None:
            groups = user.getGroups()
            if 'Anonymous' in result:
                groups = groups + ('role:Anonymous',)
            if 'Authenticated' in result:
                groups = groups + ('role:Authenticated',)
            for group in groups:
                result.append('group:%s' % group)
        # end groups
        return result
    
    # searchResults has inherited security assertions.
    # searchResults and unrestrictedSearchResults are 'borrowed' 
    # from CMFCore
    def searchResults(self, REQUEST=None, **kw):
        """ Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
            
        """
        user = getSecurityManager().getUser()
        
        # we replace, rather than append the 'allowedRolesAndUsers' index,
        # anything else would be a really big security loophole
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )
        
        return ZCatalog.searchResults(self, REQUEST, **kw)
    
    __call__ = searchResults

    security.declarePrivate('unrestrictedSearchResults')
    def unrestrictedSearchResults(self, REQUEST=None, **kw):
        """ Calls ZCatalog.searchResults directly without restrictions.

        This method returns every also not yet effective and already expired
        objects regardless of the roles the caller has.

        CAUTION: Care must be taken not to open security holes by
        exposing the results of this method to non authorized callers!

        If you're in doubt if you should use this method or
        'searchResults' use the latter.
        
        """
        return ZCatalog.searchResults(self, REQUEST, **kw)    

    security.declarePrivate('indexObject')
    def indexObject(self, object):
        """ Add to catalog.
        
        """
        url = self.__url(object)
        self.catalog_object(object, url)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object):
        """ Remove from catalog.
        
        """
        url = self.__url(object)
        self.uncatalog_object(url)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[], update_metadata=1):
        """ Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        
        """
        url = self.__url(object)
        if idxs != []:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes]
        self.catalog_object(object, url, idxs, update_metadata)

    def manage_afterAdd(self, item, container):
        # if manage_afterAdd is called but item isn't our own meta_type,
        # don't do anything!
        if item.meta_type != self.meta_type:
            return False
        
        if not hasattr(item.aq_explicit, 'Lexicon'):
            wordsplitter = Record()
            wordsplitter.group = 'Word Splitter'
            wordsplitter.name = 'HTML aware splitter'
            
            casenormalizer = Record()
            casenormalizer.group = 'Case Normalizer'
            casenormalizer.name = 'Case Normalizer'
            
            stopwords = Record()
            stopwords.group = 'Stop Words'
            stopwords.name = 'Remove listed and single char words'
            
            item.manage_addProduct['ZCTextIndex'].manage_addLexicon(
                                                 'Lexicon', 'Default Lexicon',
                                  (wordsplitter, casenormalizer, stopwords))
        
        indexes = item.indexes()
        schema = item.schema()
        
        if 'indexable_content' not in indexes:
            zctextindex_extras = Record()
            zctextindex_extras.index_type = 'Okapi BM25 Rank'
            zctextindex_extras.lexicon_id = 'Lexicon'
            # add the full text index 
            zctextindex_extras.doc_attr = 'indexable_content'
        
            item.addIndex('indexable_content',
                             'ZCTextIndex', zctextindex_extras)
        
        for index_id, index_type in (('id', 'FieldIndex'),
                                     ('meta_type', 'FieldIndex'),
                                     ('modification_time', 'DateIndex'),
                                     ('dc_creator', 'FieldIndex'),
                                     ('tags', 'KeywordIndex'),
                                     ('title', 'FieldIndex'),
                                     ('topic', 'FieldIndex'),
                                     ('group_ids', 'KeywordIndex'),
                                     ('content_type', 'FieldIndex')):
            if index_id not in indexes:
                item.addIndex(index_id, index_type)
            
        # store the common metadata for sorting
        for md in ('id', 'content_type', 'meta_type', 'title', 'topic, 'tags',
                   'size', 'modification_time', 'group_ids', 'dc_creator',
                   'indexable_summary'):
            if md not in schema:
                item.addColumn(md)
                
        return True
        
# Zope Management Methods
#
manage_addXWFCatalogForm = PageTemplateFile(
   'management/manage_addXWFCatalogForm.zpt',
    globals(), __name__='manage_addXWFCatalogForm')

def manage_addXWFCatalog(self, id, REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of XWFCatalog.
        
    """
    obj = XWFCatalog(id)
    self._setObject(id, obj)
    
    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    context.registerClass(
        XWFCatalog,
        permission='Add XWF News',
        constructors=(manage_addXWFCatalogForm,
                      manage_addXWFCatalog),
        icon='icons/ic-xwfcatalog.png'
        )
        
