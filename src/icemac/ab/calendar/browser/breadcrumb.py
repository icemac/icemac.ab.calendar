from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.breadcrumb


class CalendarBreadCrumb(icemac.addressbook.browser.breadcrumb.Breadcrumb):
    """Breadcrumb for the calendar."""

    grok.adapts(
        icemac.ab.calendar.interfaces.ICalendar,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Calendar')
