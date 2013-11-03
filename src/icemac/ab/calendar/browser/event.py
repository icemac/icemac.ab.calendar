from icemac.addressbook.i18n import _
import icemac.ab.calendar.event
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import z3c.form.button
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

    @z3c.form.button.buttonAndHandler(
        _('Clone event'), name='clone_event',
        condition=icemac.addressbook.browser.base.can_access('@@clone.html'))
    def handleCloneEvent(self, action):
        self.redirect_to_next_url('object', '@@clone.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete',
        condition=icemac.addressbook.browser.base.can_access('@@delete.html'))
    def handleDelete(self, action):
        self.redirect_to_next_url('object', '@@delete.html')


class Delete(icemac.addressbook.browser.base.BaseDeleteForm):
    """Confirmation when deleting an event."""

    label = _(u'Do you really want to delete this event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = ('datetime', 'category', 'alternative_title')


class Clone(icemac.addressbook.browser.base.BaseCloneForm):
    """Clone event with confirmation."""

    label = _(u'Do you really want to clone this event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = ('datetime', 'category', 'alternative_title')
