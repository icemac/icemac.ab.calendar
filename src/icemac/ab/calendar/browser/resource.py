from icemac.addressbook.browser.resource import base_css
import fanstatic
import icemac.ab.calendar.browser.interfaces
import js.classy
import js.jquery
import zope.viewlet.viewlet


lib = fanstatic.Library('calendar', 'resources')
calendar_css = fanstatic.Resource(lib, 'calendar.css', depends=[base_css])
print_css = fanstatic.Resource(lib, 'print.css', depends=[calendar_css])
calendar_js = fanstatic.Resource(
    lib, 'calendar.js', depends=[js.jquery.jquery, js.classy.classy],
    bottom=True)


class CalendarResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are needed for the calendar."""

    def update(self):
        calendar_css.need()
        print_css.need()
        calendar_js.need()

    def render(self):
        return u''


def set_layer(context, request):
    """Set the calendar layer on the request, so the resources are rendered."""
    zope.interface.alsoProvides(
        request, icemac.ab.calendar.browser.interfaces.ICalendarLayer)


calendar_favicon = icemac.addressbook.browser.favicon.FavIconData(
    '/fanstatic/calendar/img/favicon.ico',
    '/fanstatic/calendar/img/favicon-preview.png')
