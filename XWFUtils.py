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
__doc__ = """
A collection of generally useful utility functions.

"""

def convertCatalogResultsToXml(result_set):
    """ Convert a set of results (catalog Brain results) to XML using the
        get_xml method of those results.
       
        result_set must be an object capable of being iterated over.
    """
    xmlstream = []
    
    for result in result_set:
        file_object = result.getObject()
        xmlstream.append(file_object.get_xml())
    
    xmlstream = map(lambda x: str(x), xmlstream)

    return '\n\n'.join(xmlstream)

def convertObjectsToXml(result_set):
    """ Convert a set of objects to XML using the get_xml method of those
        objects.
       
        result_set must be an object capable of being iterated over.
    """
    xmlstream = []
    
    for result in result_set:
        xmlstream.append(result.get_xml())
    
    xmlstream = map(lambda x: str(x), xmlstream)

    return '\n\n'.join(xmlstream)
    
def createRequestFromRequest(request, filternull=1, **kws):
    # work on a copy of the form so we don't screw up the request for other
    # things
    form = request.form.copy()
    form.update(kws)
    nrequest = []
    for key,val in form.items():
        if filternull and not val: continue
        nrequest.append('%s=%s' % (key, val))
        
    return '&'.join(nrequest)

def convertTextToId(text):
    import string
    safe = string.digits + string.ascii_letters
    s = []
    for i in text:
        if i in safe:
            s.append(i)
        else:
            s.append('_')
            
    return ''.join(s)

def convertTextToAscii(text):
    s = []
    for i in text:
        if ord(i) < 128 and ord(i) > 0:
            s.append(i)
            
    return ''.join(s)
    
def removePathsFromFilenames(fname):
    """ Remove the paths from filenames uploaded by (primarily) IE.
        
    """
    return fname.split('\\')[-1].split('/')[-1]
    
def createBatch(result_set, b_start, b_size):
    b_start = int(b_start)-1; b_size = int(b_size)
    result_size = len(result_set)

    if b_start < 0:
        b_start = 0

    b_end = b_start + b_size

    if result_size <= b_end or b_end == -1:
        b_end = result_size
        
    if result_size <= b_start or b_start > b_end:
        b_start = b_end

    result_set = result_set[b_start:b_end]
    
    # it's easier to do this calculation here than in the presentation layer
    rset_size = len(result_set)
    if rset_size < b_size:
        b_end = b_start + rset_size
    else:
        b_end = b_start + b_size
    
    return (b_start, b_end, b_size, result_size, result_set) 

def generate_user_id(user_id='', first_name='', last_name='', email=''):
    if first_name and last_name:
        yield first_name+last_name[0]
        yield last_name+first_name[0]
        yield first_name+'.'+last_name
        yield last_name+'.'+first_name
    if email:
        try:
            yield email.split('@')[0]
        except:
            pass
    if user_id:
        i = 1
        while 1:
            yield user_id+'%s' % i
            i += 1
    if first_name and last_name:
        i = 1
        while 1:
            yield first_name+'.'+last_name+'%s' % i
            i += 1
