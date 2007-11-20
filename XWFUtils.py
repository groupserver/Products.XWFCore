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
from Acquisition import aq_get
from AccessControl import getSecurityManager
from App.config import getConfiguration
import re, string

import pytz
import DateTime
import datetime
try:
   # prior to zope 3.3
   from zope.datetime import parseDatetimetz
except ImportError:
   from zope.app.datetimeutils import parseDatetimetz

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

def normalize_user_id(user_id):
    import string
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
    import random
    password = ''
    for i in xrange(length):
        password += random.choice(readable_passchars)
        
    return password
    
def convert_int2b(num, base, alphabet, converted=[]):
    mod = num % 62; rem = num / 62
    converted.append(alphabet[mod])
    if rem:
        return convert_int2b(rem, 62, alphabet, converted)
    converted.reverse()

    return ''.join(converted)

def convert_int2b62(num):
    import sys, string
    alphabet = string.printable[:62]

    return convert_int2b(num, 62, alphabet, [])

def generate_accesscode(seed_string):
    """ Generate a random string for (among other things) validating users.
    
    """
    import md5, DateTime
    
    num = long(md5.new(seed_string+str(DateTime.DateTime())).hexdigest(), 16)
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
    import re, cgi
    
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

def getOption(obj, name, default=None):
    """ Get the an option, from the user object, the division config,
        or the site config.
        
    """
    security = getSecurityManager()
    user = security.getUser()
    try:
        option = user.getProperty(name, None)
    except:
        option = None
                
    if not option:    
        divConfig = getToolByName(obj, 'DivisionConfiguration', None)
        if divConfig:
            option = divConfig.getProperty(name, None)
    
    if not option:
        siteConfig = getToolByName(obj, 'GlobalConfiguration', None)
        if siteConfig:
            option = siteConfig.getProperty(name, None)
    
    return option or default

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
    if acl_users:
        user = acl_users.getUser( user_id )
    
    return user

def get_user_realnames( user_object=None, user_id='' ):
    """ If the user is real, get their preferredName, otherwise
        return some other string.
    
    """
    if user_object:
        return '%s' % (user_object.getProperty('preferredName'))

    return '%s (account removed)' % user_id

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
           ("dt is not a datetime instance, if a datetime instance was not "
            "passed in as dt, it has not been converted correctly")

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
    age = dt-today    

    # if it's after midnight in the current timezone, format it
    # without the date 
    if age.days >= 0 and age.days < 1:
        format = '%H:%M %Z'
    # if it is less than a 11 months ago (to avoid confusion
    # over the same month over two years), format it without the year
    elif age.days < 0 and age.days > -334:
        format = '%b %d %H:%M %Z'
    # otherwise format it with the year. This includes dates such as tomorrow
    # and next week, since otherwise it will not be clear that they are
    # in the future
    else:
        format = '%Y %b %d %H:%M %Z'

    return format

def munge_date(context, dt, format=None):
    timezone = getOption(context, 'timezone', 'UTC')
    dt = change_timezone(dt, timezone)

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

def get_site_by_id(context, siteId):
    assert siteId
    
    site_root = context.site_root()
    folders = ('Folder', 'Folder (Ordered)')
    sites = [s for s in site_root.Content.objectValues(folders) 
      if (s and s.getProperty('is_division', False) and s.getId() == siteId)]
    if sites:
        assert len(sites) == 1, 'Content folder is in a weird state'
        retval = sites[0]
    else:
        retval = None
    
    assert ((retval == None) or (retval.getId() == siteId))
    return retval

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

    folders = ('Folder', 'Folder (Ordered)')
    groups = [g for g in groupsFolder.objectValues(folders)
        if (g and g.getProperty('is_group', False) and g.getId() == groupId)]
    if groups:
        assert len(groups) == 1, \
          'Groups folder of %s is in a weird state' % siteId
        retval = groups[0]
    else:
        retval = None
    
    assert ((retval == None) or (retval.getId() == groupId))
    return retval

def get_support_email(context, siteId):
    assert siteId
    
    site = get_site_by_id(context, siteId)
    assert site

    support_email = getOption(context, 'supportEmail')
    retval = support_email

    if support_email == 'support@onlinegroups.net':
        supportGroupId = '%s_support' % siteId
        groupsFolder = getattr(site, 'groups')
        assert groupsFolder, "Site %s has no groups" % siteId

        folders = ('Folder', 'Folder (Ordered)')
        groups = [g for g in groupsFolder.objectValues(folders)
            if (g and g.getProperty('is_group', False) and g.getId() == supportGroupId)]

        if groups:
            assert len(groups) == 1, \
                'Groups folder of %s is in a weird state' % siteId
            group = groups[0]

            canonical = getOption(context, 'canonicalHost')
            if canonical == '%s.onlinegroups.net' % siteId:
                retval = '%s@onlinegroups.net' % supportGroupId
            elif canonical != 'onlinegroups.net':
                retval = '%s@%s' % (supportGroupId, canonical)

    assert retval
    assert '@' in retval
    return retval
    
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
    
