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
    
def convertTextToAscii(text):
    s = []
    for i in text:
        if ord(i) < 128:
            s.append(i)
            
    return ''.join(s)
    
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
