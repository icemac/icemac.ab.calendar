# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.browser.resource import base_css
import fanstatic
import icemac.ab.calendar.browser.interfaces
import os.path
import zope.viewlet.viewlet


css_lib = fanstatic.Library('calendar_css', 'resources')
calendar_css = fanstatic.Resource(css_lib, 'calendar.css', depends=[base_css])


class CalendarResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are needed for the calendar."""

    def update(self):
        calendar_css.need()

    def render(self):
        return u''


def set_layer(context, request):
    """Set the calendar layer on the request, so the resources are rendered."""
    zope.interface.alsoProvides(
        request, icemac.ab.calendar.browser.interfaces.ICalendarLayer)
