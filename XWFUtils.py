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