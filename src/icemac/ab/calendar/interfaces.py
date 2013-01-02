# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import zope.interface


class ICalendar(zope.interface.Interface):
    """Calender and storage for dates."""


class ICalendarProvider(zope.interface.Interface):
    """Marker interface for objects providing a calendar on an attribute.

    This is necessary to meet security which otherwise raises a ForbiddenError.

    """
    calendar = zope.interface.Attribute(u'ICalendar')

