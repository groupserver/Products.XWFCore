# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from AccessControl import ModuleSecurityInfo

xwfutils_security = ModuleSecurityInfo('Products.XWFCore.XWFUtils')
xwfutils_security.declarePublic('convertCatalogResultsToXml')
xwfutils_security.declarePublic('convertObjectsToXml')
xwfutils_security.declarePublic('createRequestFromRequest')
xwfutils_security.declarePublic('convertTextToAscii')
xwfutils_security.declarePublic('createBatch')