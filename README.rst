Introduction
============

This is the core code for the old *XML Work Flow* (XWF) system. For the
most part, GroupServer_ uses this product for the ``XWFUtils`` module,
which contains many useful utilities.

``XWFUtils``
============

While it contains many utilities, the ``XWFUtils`` module only contains a
few useful utilities.

``Products.XWFCore.XWFUtils.add_marker_interfaces``:
  Add a marker-interface to an object in the ZMI.

``Products.XWFCore.XWFUtils.change_timezone``:
  Change a timestamp to a particular timezone. It works with timestamps of
  various types: ``float``, ``int``, ``datetime.datetime``, and
  ``DateTime.DateTime``.

``Products.XWFCore.XWFUtils.comma_comma_and``:
  Turns a sequence of strings into one string, where each element is
  separated by a comma (except for the last, which is separated from the
  others by an ``and``).

``Products.XWFCore.XWFUtils.curr_time``:
  Gets the current time in UTC.

``Products.XWFCore.XWFUtils.convert_int2b62``:
  Converts an integer to a base-64 encoded string.

``Products.XWFCore.XWFUtils.dt_to_user_timezone``:
  Converts a date-time to one in the preferred timezone of the user.

``Products.XWFCore.XWFUtils.getOption``:
  Get an option, walking the sequence user, site, installation,
  default. Being replaced by the ``gs.option`` product.
  

``Products.XWFCore.XWFUtils.get_support_email``:
  Gets the email address of the support-group for the site. Being replaced
  with the ``siteInfo.get_support_email()`` call.

``Products.XWFCore.XWFUtils.munge_date``:
  Converts a timestamp into a string, in the user's current timezone. The
  date is displayed as ``hour:minute:second`` if it is less than a day old,
  ``month day hour:minute:second`` if it is less than eleven months old, or
  with the year otherwise.

``Products.XWFCore.XWFUtils.removePathsFromFilenames``:
  Microsoft Internet Explorer used to add the full-path to file names that
  were uploaded with the file-widget. This utility removes them.

TODO
----

The utilities need to be split in three: those that are generally useful for
Python-based systems in general (``gs.core.utils``), those that require
Zope (``gs.base.utils``), and those to do with dates (``gs.profile.tz``).

.. _GroupServer: http://groupserver.org/

..  LocalWords:  XWF XWFUtils timestamp
