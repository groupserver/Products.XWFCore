# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2003, 2004 IOPEN Technologies Ltd
# Copyright 2013, 2015 OnlineGroups.net and Contributors.
#
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
"""
A collection of generally useful utility functions.

"""
import os
import random
import cgi
from Acquisition import aq_get
from App.config import getConfiguration
from AccessControl import getSecurityManager
from gs.cache import cache

import re
import string

import pytz

import DateTime
import datetime
import time

try:
    from hashlib import md5
except ImportError:
    from md5 import md5  # lint:ok

import logging
log = logging.getLogger('XWFCore.XWFUtils')

try:
    # prior to zope 3.3
    from zope.datetime import parseDatetimetz
except ImportError:
    from zope.app.datetimeutils import parseDatetimetz  # lint:ok


def locateDataDirectory(component, subpaths=()):
    """ Create and return the string representing the data directory for
    a given component, eg. groupserver.GSFeedParser

    """
    config = getConfiguration()
    client_home = config.clienthome

    assert os.path.isdir(client_home), \
              'Directory "%s" does not exist' % client_home

    data_dir = os.path.join(client_home, 'groupserver.data',
                            component, *subpaths)

    if not os.path.isdir(data_dir):
        os.makedirs(data_dir, 0700)

    return data_dir


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
        if filternull and not val:
            continue
        nrequest.append('%s=%s' % (key, val))

    return '&'.join(nrequest)


def convertTextToId(text):
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
        if ((ord(i) < 128 and ord(i) > 31) or
            (ord(i) in (9,10,13))):
            s.append(i)

    return ''.join(s)


def try_encoding(s, possible_encoding, encoding):
    success = False
    for try_encoding in (possible_encoding, 'utf-8', 'iso-8859-1', 'iso-8859-15'):
            try:
                s = s.decode(try_encoding)
                s.encode(encoding)
                success = True
                break
            except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
                pass

    if success:
        return s

    raise UnicodeDecodeError


def convertTextUsingContentType(text, ct, encoding='UTF-8'):
    """ Given some text, and the content-type field of an email,
        try and re-encode it as the given encoding.

    """
    if ct:
        encoding_match = re.search('charset=[\'\"]?(.*?)[\'\"]?;', ct)
        poss_encoding = encoding_match and encoding_match.groups()[0] or 'ascii'
    else:
        poss_encoding = 'ascii'

    try:
        text = try_encoding(text, poss_encoding, encoding)
    except UnicodeDecodeError:
        text = convertTextToAscii(text)

    # strip most control characters, XML no like :)
    text = re.sub('[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)

    return text


def removePathsFromFilenames(fname):
    """ Remove the paths from filenames uploaded by (primarily) IE.

    """
    retval = fname.split('\\')[-1].split('/')[-1]
    retval = retval.replace('\r', ' ').replace('\n',' ').replace('\t',' ')
    assert type(retval) in (unicode, str)
    return retval


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

def normalize_user_id(user_id):
    valid_chars = string.ascii_letters+string.digits+'-'+'_'
    id_chars = []
    for char in user_id:
        if char in valid_chars:
            id_chars.append(char)

    return ''.join(id_chars)

def generate_user_id(user_id='', first_name='', last_name='', email=''):
    nuid = normalize_user_id
    if first_name and last_name:
        yield nuid((first_name+last_name).lower())
        yield nuid((last_name+first_name).lower())
        yield nuid((first_name+last_name[0]).lower())
        yield nuid((last_name+first_name[0]).lower())
        yield nuid((first_name+'.'+last_name).lower())
        yield nuid((last_name+'.'+first_name).lower())
    if email:
        try:
            yield nuid((email.split('@')[0]).lower())
        except:
            pass
    if user_id:
        i = 1
        while 1:
            yield nuid((user_id+'%s' % i).lower())
            i += 1
    if first_name and last_name:
        i = 1
        while 1:
            yield nuid((first_name+'.'+last_name+'%s' % i).lower())
            i += 1
    if email:
        try:
            uid = (email.split('@')[0]).lower()
            i = 1
            while 1:
                yield nuid(uid+'%s' % i)
                i += 1
        except:
            pass

readable_passchars = ['%', '+', '2', '3', '4', '5',
                      '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
                      'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S',
                      'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'b', 'c', 'd', 'e',
                      'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                      'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def generate_password(length=8):
    password = ''
    for i in xrange(length): #@UnusedVariable
        password += random.choice(readable_passchars)

    return password

def convert_int2b(num, alphabet, converted=[]):
    mod = num % len(alphabet); rem = num / len(alphabet)
    converted.append(alphabet[mod])
    if rem:
        return convert_int2b(rem, alphabet, converted)
    converted.reverse()
    retval = ''.join(converted)
    return retval

def convert_int2b62(num):
    alphabet = string.printable[:62]
    retval = convert_int2b(num, alphabet, [])
    return retval

def generate_accesscode(seed_string):
    """ Generate a random string for (among other things) validating users.

    """
    num = long(md5(seed_string+str(datetime.datetime.now().isoformat())).hexdigest(), 16)
    access_code = convert_int2b62(num)

    return access_code

def assign_ownership(object, owner, recursive=0, acl_user_path='/acl_users'):
    """ Change the ownership to a user with Manager priviledges.

    """
    acl_users = object.unrestrictedTraverse(acl_user_path)
    user = acl_users.getUser(owner)

    # for some zope-magic reason, the user returned by acl_users
    # isn't context wrapped
    user = user.__of__(acl_users)

    if not user.has_permission('Take ownership', object):
        return 0

    object.changeOwnership(user, recursive)

    return 1

def markupEmail(text):
    text = cgi.escape(text)
    text = re.sub('(?i)(http://|https://)(.+?)(\&lt;|\&gt;|\)|\]|\}|\"|\'|$|\s)',
           '<email:link url="\g<1>\g<2>">\g<1>\g<2></email:link>\g<3>',
           text)
    text = text.replace('@', ' ( at ) ')

    return text

# getToolByName is borrowed directly from CMFCore, since we want to achieve
# _exactly_ the same goal
_marker = []
def getToolByName(obj, name, default=_marker):

    """ Get the tool, 'toolname', by acquiring it.

    o Application code should use this method, rather than simply
      acquiring the tool by name, to ease forward migration (e.g.,
      to Zope3).
    """
    try:
        tool = aq_get(obj, name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default
    else:
        if tool is _marker:
            raise AttributeError, name
        return tool

def getOption(obj, name, default=None, user=None):
    """ Get the an option, from the user object, the division config,
        or the site config.

    """
    if not user:
        security = getSecurityManager()
        user = security.getUser()

    try:
        option = user.getProperty(name, None)
    except:
        option = None

    if option == None:
        divConfig = getToolByName(obj, 'DivisionConfiguration', None)
        if divConfig:
            option = divConfig.getProperty(name, None)

    if option == None:
        siteConfig = getToolByName(obj, 'GlobalConfiguration', None)
        if siteConfig:
            option = siteConfig.getProperty(name, None)

    if option == None:
        retval = default
    else:
        retval = option
    return retval

def getNotificationTemplate(obj, n_type, n_id):
    site_root = obj.site_root()
    presentation = site_root.Templates.email.notifications.aq_explicit

    ptype_templates = getattr(presentation, n_type, None)
    if not ptype_templates:
        return None

    ignore_ids = getattr(ptype_templates, 'ignore_ids', [])
    if n_id in ignore_ids:
        return None

    template = (getattr(ptype_templates.aq_explicit, n_id, None) or
                getattr(ptype_templates.aq_explicit, 'default', None))

    if not template:
        return None

    return template

def get_user( context, user_id ):
    acl_users = getToolByName( context, 'acl_users', None )
    user = None
    if acl_users and user_id:
        user = acl_users.getUser( user_id )

    return user

def get_user_realnames( usr=None, user_id='', context=None ):
    """ If the user is real, get their fn, otherwise
        return some other string.

    """
    # assert (usr != None) or (user_id != ''), 'Must supply a user or user id'
    if not(usr) and context:
        usr = get_user(context, user_id)
    if usr:
        fn = usr.getProperty('fn')
        if not fn:
            fn = usr.getProperty('preferredName')
    else:
        fn = '%s (account removed)' % user_id
    retval = '%s' % fn
    assert retval, \
      'No retval when given usr %s and user_id %s' % (usr, user_id)
    assert type(retval) in (str, unicode)
    return retval

def rfc822_date(dt, interval=0):
    """ Convert a UTC datetime object into an RFC 822 formatted date, optionally
    shifted by an interval.

    """
    if interval:
        dt = dt+datetime.timedelta(interval)

    # pinched from the rfc822 library
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
            dt.day,
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
            dt.year, dt.hour, dt.minute, dt.second)

def change_timezone(dt, timezone):
    # if we are a float, make the (rather dubious) assumption that we're
    # looking at a UTC timestamp
    if isinstance(dt, float) or isinstance(dt, int):
        dt = datetime.datetime.fromtimestamp(dt, pytz.utc)
    # check to make sure we're not a Zope DateTime object
    elif isinstance(dt, DateTime.DateTime):
        dt = dt.toZone('UTC')
        dt = datetime.datetime(dt._year, dt._month, dt._day, dt._hour,
                               dt._minute, int(dt._nearsec),
                               int((dt._second-dt._nearsec) * 1000000),
                               tzinfo=pytz.utc)
    elif isinstance(dt, str) or isinstance(dt, unicode):
        # if we have the format Sat, 10 Mar 2007 22:47:20 +1300 (NZDT)
        # strip the (NZDT) bit before parsing, otherwise we break the parser
        dt = re.sub(' \(.*?\)','', dt)
        dt = parseDatetimetz(dt)

    assert isinstance(dt, datetime.datetime), \
           ("dt is not a datetime instance (is a %s), if a datetime "\
            "instance was not "\
            "passed in as dt, it has not been converted correctly" %\
            dt)

    tz = pytz.timezone(timezone)
    return tz.normalize(dt.astimezone(tz))


def date_format_by_age(dt):
    # find out the timezone of our datetime object -- we used to pass this
    # in, but this way we guarantee that our datetime isn't a tz naive instance
    # and that we never do an incorrect comparison
    tzinfo = dt.tzinfo

    # set a date format according to it's distance from the present
    utcnow = datetime.datetime.now(pytz.UTC)
    now = utcnow.astimezone(tzinfo)

    today = datetime.datetime(now.year, now.month, now.day,
                              tzinfo=tzinfo)
    age = dt - today

    # if it's after midnight in the current timezone, format it
    # without the date
    if age.days >= 0 and age.days < 1:
        retval = '%l:%M%P'
    # if it is less than a 11 months ago (to avoid confusion
    # over the same month over two years), format it without the year
    elif age.days < 0 and age.days > -334:
        retval = '%l:%M%P, %b %d'
    # otherwise format it with the year. This includes dates such as tomorrow
    # and next week, since otherwise it will not be clear that they are
    # in the future
    else:
        retval = '%l:%M%P, %b %d, %Y'
    return retval


def dt_to_user_timezone(context, dt, user):
    timezone = getOption(context, 'tz', user=user)
    timezone = timezone and timezone or 'UTC'
    retval = change_timezone(dt, timezone)
    return retval

def munge_date(context, dt, format=None, user=None):
    dt = dt_to_user_timezone(context, dt, user)

    # if we don't have the format try and get the format from the options
    if not format:
        format = getOption('date_format', None)

    # otherwise set it according to the age of the timestamp
    if not format:
        format = date_format_by_age(dt)

    return dt.strftime(format)

def all_timezones():
    return pytz.all_timezones

def curr_time():
    return datetime.datetime.now(pytz.utc)

def get_current_virtual_site(context):
    while context:
        try:
            in_site = context.getProperty('is_division')
            if in_site:
                break
        except AttributeError:
            pass
        context = context.aq_parent

    return context.aq_explicit

def get_virtual_site_objects(context, current_first=True):
    site_root = context.site_root()

    objects = []
    for object_id in site_root.Content.objectIds(('Folder', 'Folder (Ordered)')):
        object = site_root.Content.restrictedTraverse(object_id, None)
        if object:
            try:
                if object.getProperty('is_division', False):
                    objects.append(object)
            except:
                pass

    if current_first:
        current_site = get_current_virtual_site(context)
        if current_site:
            try:
                objects.remove(current_site)
            except ValueError:
                pass
            objects.insert(0, current_site)

    return objects

def get_site_by_id(context, siteId):
    assert siteId

    site_root = context.site_root()

    site = getattr(site_root.Content, siteId, None)
    if site and site.getProperty('is_division', False):
        retval = site
    else:
        retval = None

    return retval

def ck_simple(*args):
    instance_id = 'foo'
    ck = ':'.join((instance_id,)+args[1:])
    print ck
    return ck

@cache('utils.get_group_metadata_by_id', ck_simple, 120)
def get_group_metadata_by_id(context, groupId):
    """ Get the metadata of a group by it's ID.

    """
    vsites = get_virtual_site_objects(context)

    top = time.time()
    log.info("Populating GroupMetadataCache")
    for site in vsites:
        groups = getattr(site, 'groups', None)
        if groups and getattr(groups, 'is_groups', False):
            if groups.hasObject(groupId):
                poss_group = getattr(groups.aq_explicit, groupId)
                if poss_group.getProperty('is_group', False):
                    metadata = {'title': poss_group.title_or_id(),
                                'site': site.getId()}

                    bottom = time.time()
                    log.info("Breaking early populating GroupMetadataCache, took %s ms" % ((bottom-top)*1000.0))

                    return metadata

    bottom = time.time()
    log.info("Looked through all sites, but didn't find group, took %s secs" % (bottom-top))

    return None

def get_group_by_siteId_and_groupId(context, siteId, groupId):
    """Get Web-Group by ID

    Returns the Web-instance, rather than the mailing-list instance or the
    user-group instance, of a group. Yes, "group" is ambiguous.

    Sorry about the long function name. Miss Java?
    """
    assert groupId

    site = get_site_by_id(context, siteId)

    groupsFolder = getattr(site, 'groups')
    assert groupsFolder, 'The site %s has no groups' % siteId

    group = getattr(groupsFolder, groupId, None)

    if group and group.getProperty('is_group', False):
        retval = group
    else:
        retval = None

    return retval

def get_support_email(context, siteId):
    if not siteId:
        log.warning("get_support_email called from outside site context, unable to return a support email, so returning support@")
        return "support@"

    site = get_site_by_id(context, siteId)
    assert site

    support_email = getOption(context, 'supportEmail')
    retval = support_email

    # AM: Temporarily directing all OGN support queries to
    #  support@onlinegroups.net
    #if support_email == 'support@onlinegroups.net':
    if False:
        groupsFolder = getattr(site, 'groups')
        assert groupsFolder, "Site %s has no groups" % siteId

        folders = ('Folder', 'Folder (Ordered)')
        groups = [g for g in groupsFolder.objectValues(folders)
            if (g and g.getProperty('is_group', False) and
              (g.getProperty('group_template', '') == 'support'))]

        if groups:
            assert len(groups) == 1, \
                'Groups folder of %s is in a weird state' % siteId
            group = groups[0]
            supportGroupId = group.getId()

            canonical = getOption(group, 'canonicalHost')
            if canonical == '%s.onlinegroups.net' % siteId:
                retval = '%s@onlinegroups.net' % supportGroupId
            elif canonical != 'onlinegroups.net':
                retval = '%s@%s' % (supportGroupId, canonical)

    if retval and '@' not in retval:
        log.warning("support email is not set correctly: %s. This may be an error, or it may be normal if the page triggering this is outside the normal environment, such as a ZMI or other error." % retval)
    return retval

def get_document_metadata(document):
    """ Get Document Metadata

        Given a document, return a dictionary of
        values: title, size (in KB) and content-type.
    """
    assert document, "No document provided"

    doc_title = document.title_or_id()
    doc_size = document.get_size() / 1024
    doc_content = document.getContentType()

    retval = {
        'title' : doc_title,
        'size'  : doc_size,
        'type'  : doc_content
    }
    return retval

def generate_verification_id(email):
    """ Given an email address, generate a verification id
    """
    assert email, "No email address provided"

    # Let us hope that the verification ID *is* unique
    vNum = long(md5(time.asctime() + email).hexdigest(), 16)
    verificationId = str(convert_int2b62(vNum))
    return verificationId

def users_can_join_group(groupId, reasonNeeded=False):
    """ Given a group, return whether the group is
        is in a joinable state
    """
    assert groupId, "No group ID provided"

    if reasonNeeded:
        retval = (True, (100, 'Users can always join'))
    else:
        retval = True
    assert retval
    return retval

def entity_exists(context, entityId):
    '''Check whether something with this id already exists
    '''
    assert entityId, 'No entity id provided'

    site_root = context.site_root()
    assert site_root, 'Could not find site root'

    # Does a site exist with id entityId?
    assert hasattr(site_root, 'Content'), 'No Content'
    sitesContainer = site_root.Content
    siteIds = [ s[0] for s in sitesContainer.objectItems('Folder') if s[1].getProperty('is_division', False) ]
    if entityId in siteIds:
        return 1

    # Does a group exist with id entityId?
    assert hasattr(site_root, 'ListManager'), 'No ListManager'
    listManager = site_root.ListManager
    groupIds = [ m[0] for m in listManager.objectItems('XWF Mailing List') ]
    if entityId in groupIds:
        return 2

    # Does a user exist with id entityId?
    assert hasattr(site_root, 'acl_users'), 'No acl_users'
    if site_root.acl_users.getUserById(entityId):
        return 3

    # The following two checks should *NOT* hold if we have got this far.
    # 1. Check in ACL Users
    try:
        site_root.acl_users.getGroupById('%s_member' % entityId)
    except:
        pass
    else:
        return 4

    # 2. Check in the add_group email template
    assert hasattr(site_root, 'Templates'), 'No Templates'
    addGroupNotification = site_root.Templates.email.notifications.add_group
    ids = list(addGroupNotification.getProperty('ignore_ids'))
    if '%s_member' % entityId in ids:
        return 5

    # If we are here, then all is well in the world

    return False

def add_marker_interfaces(object, interfaces):
    ''' Add given marker interfaces to a given object.
    '''
    from Products.Five.utilities.interfaces import IMarkerInterfaces
    adapted_to_marker = IMarkerInterfaces(object)
    add = adapted_to_marker.dottedToInterfaces(interfaces)
    adapted_to_marker.update(add=add)

    return True

def remove_marker_interfaces(object, interfaces):
    ''' Remove given marker interfaces from a given object.
    '''
    from Products.Five.utilities.interfaces import IMarkerInterfaces
    adapted_to_marker = IMarkerInterfaces(object)
    remove = adapted_to_marker.dottedToInterfaces(interfaces)
    adapted_to_marker.update(remove=remove)

    return True

def sort_by_name(a, b):
    assert hasattr(a, 'name')
    assert hasattr(b, 'name')

    if (a.name.lower() < b.name.lower()):
        retval = -1
    elif (a.name.lower() == b.name.lower()):
        retval =  0
    else:#a.name.lower() > b.name.lower()
        retval =  1

    assert type(retval) == int
    return retval


def timedelta_to_string(td):
    '''Convert a time delta to a Unicode string.

    Inspired by Recipe 498062
      http://code.activestate.com/recipes/498062/

    ARGUMENTS
      td:   Time delta

    RETURNS
      A Unicode string, representing the time-delta.

    SIDE EFFECTS
      None'''
    assert isinstance(td, datetime.timedelta)
    deltas = []
    s = int(td.days * 86400 + td.seconds)
    #              Unit     Seconds
    unitLimits = [("year",  31536000),
                  ("month",  2592000),
                  ("week",    604800),
                  ("day",      86400),
                  ("hour",      3600),
                  ("minute",      60),
                  ("second",       1)]
    for unit, limit in unitLimits:
        tdInUnit = s/limit
        if tdInUnit:
            if (tdInUnit > 1):
                # Plural
                deltas.append(u'%d %ss' % (tdInUnit, unit))
            else:
                deltas.append(u'%d %s' % (tdInUnit, unit))
            s = s - (tdInUnit * limit)
    retval = comma_comma_and(deltas)
    assert type(retval) == unicode
    return retval

def comma_comma_and(l, conj='and'):
    '''Join a list of strings joined with commas and a conjunction
       (either "and" or "or", defaulting to "and").

      Turn a list (or tuple) of strings into a single string, with all
      the items joined by ", " except for the last two, which are joined
      by either " and " or " or ". If there is only one item in the list,
      it is returned.
    '''
    assert type(l) in [list, tuple], '%s, not a list or tuple' % type(l)
    if len(l) == 0:
        retval = u''
    elif len(l) == 1:
        retval = l[0]
    else:
        base = u' and '
        if conj.strip() == 'or':
            base = u' or '
        retval = base.join((u', '.join(l[:-1]), l[-1]))
    assert type(retval) in (unicode, str)
    return retval

deprecationTracking = {}
def deprecated(context, script, message=''):
    """ Logging for deprecated scripts.

    """
    path = '/'.join(script.getPhysicalPath())
    url = getattr(context.REQUEST, 'URL', '##UNKNOWN##')
    key = path
    if deprecationTracking.has_key(key):
        # shortcut. We only report a deprecation once per instance per start.
        # pretty much this only makes it useful to know that it is still
        # being used. Switch this off when fixing.
        return
    else:
        # we don't lock, because we don't care *that* much if we print a message
        # more than once.
        deprecationTracking[key] = True

    m = 'Deprecated script "%s" called from "%s".'
    if message:
        m += ' %s.' % message
    log.warn(m % (path, url))
    # print traceback.print_stack()
    # assert False, 'Here!'

# --=mpj17=-- My God, this is an awful place.
#
# TODO: Remove this function when we no longer lave to run on Zope 2.10.
#
# Sometimes Zope acquisition can be a hideous pain.
# This is one of those times. For whatever reason, self.context
# gets all wrapped up in some voodoo to do with
# "Products.Five.metaclass". In Zope 2.10 the "aq_self" is
# required to exorcise the Dark Magiks and to allow the code to
# operate without spewing errors about the site-instance being
# None. However, in Zope 2.13 this causes a LocationError to be
# thrown. It is the job of this class to do the right thing no
# matter what bullshit Zope acquisition decides to throw at us.
#
# What "get_the_actual_instance_from_zope" does is a bit of a mystery,
# and I wrote the damn thing. Only use it if you have to, is a good
# rule of thumb.
#
# Basically, this is a CPP-like #ifdef
try:
    from five.formlib.formbase import PageForm  # lint:ok
except:
    zope_213 = False
else:
    zope_213 = True


def get_the_actual_instance_from_zope(instance):
    assert hasattr(instance, 'aq_self'),\
        'The %s instance %s has no aq_self attribute' % (type(instance), instance)
    assert type(zope_213) == bool

    if zope_213:
        retval = instance
    else:
        retval = instance.aq_self

    assert retval
    return retval


def abscompath(component, relativepath):
    """ From a component and a relative path, calculate the absolute path to a
        file.

        Usage: abscompath(gs.group.home, "browser/template/page.pt")

    """
    componentpath = os.path.dirname(component.__file__)

    path = os.path.join(componentpath, relativepath)

    return unicode(path)


# Wrap format_excec for older ZMI-side scripts.
from traceback import format_exc as actual_format_exec


def format_exec():
    return actual_format_exec()


def object_values(ocontainer, otypes=()):
    """ This is effectively a wrapped version of OFS.objectValues, but
        checking permission for each object.
    """
    objects = []
    if not ocontainer:
        return objects

    for object_id in ocontainer.objectIds(otypes):
        try:
            obj = getattr(ocontainer, object_id)
            objects.append(obj)
        except:
            pass

    return objects
