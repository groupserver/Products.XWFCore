# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2003, 2004 IOPEN Technologies Ltd, 2013 OnlineGroups.net and
# Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

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
xwfutils_security.declarePublic('object_values')

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

from odict import ODict  # lint:ok

from AccessControl import allow_module
allow_module('traceback')
