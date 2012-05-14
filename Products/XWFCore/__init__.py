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
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

xwfutils_security = ModuleSecurityInfo('Products.XWFCore.XWFUtils')
xwfutils_security.declarePublic('convertCatalogResultsToXml')
xwfutils_security.declarePublic('convertObjectsToXml')
xwfutils_security.declarePublic('createRequestFromRequest')
xwfutils_security.declarePublic('convertTextToAscii')
xwfutils_security.declarePublic('createBatch')
xwfutils_security.declarePublic('generate_user_id')
xwfutils_security.declarePublic('assign_ownership')
xwfutils_security.declarePublic('markupEmail')
xwfutils_security.declarePublic('getToolByName')
xwfutils_security.declarePublic('convertTextUsingContentType')
xwfutils_security.declarePublic('rfc822_date')
xwfutils_security.declarePublic('change_timezone')
xwfutils_security.declarePublic('all_timezones')
xwfutils_security.declarePublic('munge_date')
xwfutils_security.declarePublic('curr_time')
xwfutils_security.declarePublic('getOption')
xwfutils_security.declarePublic('get_site_by_id')
xwfutils_security.declarePublic('get_group_by_siteId_and_groupId')
xwfutils_security.declarePublic('get_support_email')
xwfutils_security.declarePublic('convert_int2b62')
xwfutils_security.declarePublic('get_user_realnames')
xwfutils_security.declarePublic('get_document_metadata')
xwfutils_security.declarePublic('generate_verification_id')
xwfutils_security.declarePublic('users_can_join_group')
xwfutils_security.declarePublic('entity_exists')
xwfutils_security.declarePublic('add_marker_interfaces')
xwfutils_security.declarePublic('remove_marker_interfaces')
xwfutils_security.declarePublic('sort_by_name')
xwfutils_security.declarePublic('comma_comma_and')
xwfutils_security.declarePublic('timedelta_to_string')
xwfutils_security.declarePublic('deprecated')
xwfutils_security.declarePublic('format_exec')

csv_security = ModuleSecurityInfo('Products.XWFCore.CSV')
csv_security.declarePublic('CSVFile')

from Products.XWFCore.CSV import CSVFile
allow_class(CSVFile)

def initialize(context):
    # Import lazily, and defer initialization to the module
    import XWFCatalog
    XWFCatalog.initialize(context)

validator_security = ModuleSecurityInfo('Products.XWFCore.validators')
validator_security.declarePublic('validate_email')
validator_security.declarePublic('ValidationError')

from odict import ODict

from AccessControl import allow_module
allow_module('traceback')

