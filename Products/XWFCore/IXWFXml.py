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
from zope.interface.interface import Interface

class IXmlProducer(Interface):
    def get_xml(): #@NoSelf
        """ Returns a stream of XML representative of the object.
        
        """
        
    def get_xmlMetadataElements(default_ns=''): #@NoSelf
        """ Returns a stream of XML representative of the metadata of the
        object.
        
        For example, if the object contains metadata attributes 'dc:Title',
        'dc:Description' and 'id', and the default_ns passed is 'foo',
        the metadata stream would be:
        
        <dc:Title>Some title</dc:Title>
        <dc:Description>Some description</dc:Description>
        <foo:id>ObjectID</foo:id>
        
        """
    
