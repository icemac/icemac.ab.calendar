from icemac.addressbook.i18n import _
import icemac.ab.calendar.event
import icemac.addressbook.browser.base


class Add(icemac.addressbook.browser.base.BaseAddForm):
    """Add form for an event."""

    label = _(u'Add new event')
    interface = icemac.ab.calendar.interfaces.IEvent
    class_ = icemac.ab.calendar.event.Event
    next_url = 'parent'
