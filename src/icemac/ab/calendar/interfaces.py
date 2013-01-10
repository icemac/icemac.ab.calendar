# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import zope.interface


class ICalendar(zope.interface.Interface):
    """Calender and storage for dates."""


class ICalendarProvider(zope.interface.Interface):
    """Marker interface for objects providing a calendar on an attribute.

    This is necessary to meet security which otherwise raises a ForbiddenError.

    """
    calendar = zope.interface.Attribute(u'ICalendar')


class ICategories(zope.interface.Interface):
    """Container for event categories."""


class ICategory(zope.interface.Interface):
    """An event category."""

    title = zope.schema.TextLine(title=_(u'event category'))


class ICalendarMasterData(zope.interface.Interface):
    """Marker interface for objects providing a calendar master data

    This is necessary to meet security which otherwise raises a ForbiddenError.

    """
    calendar_categories = zope.interface.Attribute(u'ICategories')
