from icemac.addressbook.i18n import _
import icemac.ab.calendar.event
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import z3c.form.form


class Add(icemac.addressbook.browser.base.BaseAddForm):
    """Add form for an event."""

    label = _(u'Add new event')
    interface = icemac.ab.calendar.interfaces.IEvent
    class_ = icemac.ab.calendar.event.Event
    next_url = 'parent'


class Edit(icemac.addressbook.browser.base.GroupEditForm):
    """Edit for for an event."""

    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    label = _('Edit event')
    interface = icemac.ab.calendar.interfaces.IEvent
    next_url = 'parent'
    z3c.form.form.extends(icemac.addressbook.browser.base.GroupEditForm,
                          ignoreFields=True)
