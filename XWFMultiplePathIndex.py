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
from Products.PluginIndexes.PathIndex.PathIndex import *
from types import StringType
from zLOG import LOG, ERROR

class MultiplePathIndex(PathIndex):
    def index_object(self, documentId, obj ,threshold=100):
        """ hook for (Z)Catalog.
            
             Much of this method is taken from the PathIndex PluginIndex supplied
             by Zope Corporation.
             
             Rather than taking a single path, or tuple of path parts, MultiplePathIndex
             expects to receive a _tuple_ of single paths, or a tuple of tuples of path parts.
             
        """
        f = getattr(obj, self.id, None)
        if f:
            if safe_callable(f):
                try:
                    paths = f()
                except AttributeError:
                    return 0
            else:
                paths = f
            if not paths:
                paths = []
            if type(paths) not in (ListType, TupleType):
                raise TypeError('paths value must be tuple of strings, or tuple of tuples of strings')
        else:
            return 0
        
        for path in paths:
            if type(path) in (ListType, TupleType):
                path = '/'+ '/'.join(path[1:])
            elif not type(path) == StringType:
                raise TypeError('path value must be string or tuple of strings')
                                                                                
            comps = filter(None, path.split('/'))
            
            if not self._unindex.has_key(documentId):
                self._migrate_length()
                self._length.change(1)
            
            for i in range(len(comps)):
                self.insertEntry(comps[i], documentId, i)
            
            if self._unindex.has_key(documentId):
                if path not in self._unindex[documentId]:
                    self._unindex[documentId].append(path)
                    self._p_changed = 1
            else:
                self._unindex[documentId] = [path]
                                                                            
        return 1
             
    def unindex_object(self, documentId):
        """ hook for (Z)Catalog.
            
            Much of this method is taken from the PathIndex PluginIndex supplied by
            Zope Corporation.
            
            Rather than taking a single path, or tuple of path parts, MultiplePathIndex
            expects to receive a _tuple_ of single paths, or a tuple of tuples of path parts.
            
        """
        if not self._unindex.has_key(documentId):
            LOG(self.__class__.__name__, ERROR,
                'Attempt to unindex nonexistent document'
                 ' with id %s' % documentId)
            return
            
        paths = self._unindex[documentId]
        for path in paths:
            comps = path.split('/')
            
            for level in range(len(comps[1:])):
                comp = comps[level+1]
 
                try:
                    self._index[comp][level].remove(documentId)
                        
                    if not self._index[comp][level]:
                        del self._index[comp][level]
                    
                    if not self._index[comp]:
                        del self._index[comp]
                except KeyError:
                    LOG(self.__class__.__name__, ERROR,
                        'Attempt to unindex document'
                        'with id %s failed' % documentId)
  
        self._migrate_length()
        self._length.change(-1)
        del self._unindex[documentId]
