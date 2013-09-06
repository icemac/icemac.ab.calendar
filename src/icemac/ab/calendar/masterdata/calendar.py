import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import zope.schema.interfaces


class CalendarView(icemac.addressbook.browser.base.GroupEditForm):
    """Edit the calendar view settings."""

    interface = icemac.ab.calendar.interfaces.ICalendarDisplaySettings
    next_url = 'parent'


class AnnotationField(icemac.addressbook.browser.datamanager.AnnotationField,
                      grok.MultiAdapter):
    """Special AnnotationField for calendar."""

    grok.adapts(icemac.ab.calendar.interfaces.ICalendar,
                zope.schema.interfaces.IField)

    no_security_proxy = (
        icemac.ab.calendar.interfaces.ICalendarDisplaySettings,)
