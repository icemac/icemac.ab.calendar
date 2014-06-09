from datetime import date
from icemac.addressbook.i18n import _
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.event
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import z3c.form.button
import z3c.form.form
import zope.component
import zope.traversing.browser


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
        self.redirect_to_next_url('object', 'clone.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete',
        condition=icemac.addressbook.browser.base.can_access('@@delete.html'))
    def handleDelete(self, action):
        self.redirect_to_next_url('object', 'delete.html')


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


class CustomizeRecurredEvent(icemac.ab.calendar.browser.base.View):
    """Prepare customization of a RecurredEvent."""

    def __call__(self):
        self.session['recurring-event-name'] = self.request.form['event']
        self.session['recurred-event-date'] = date(
            *tuple(int(x) for x in self.request.form['date'].split('-')))
        self.request.response.redirect(
            self.url(self.context, 'addFromRecurredEvent.html'))
        return ''


class AddFromRecurredEvent(icemac.ab.calendar.browser.base.View,
                           icemac.addressbook.browser.base.BaseAddForm):
    """Add form for changing a recurred event."""

    label = _(u'Edit recurred event')
    interface = icemac.ab.calendar.interfaces.IEvent
    class_ = icemac.ab.calendar.event.Event
    next_url = 'parent'
    ignoreContext = False
    buttons = z3c.form.button.Buttons()
    handlers = z3c.form.button.Handlers()

    def getContent(self):
        recurring_events = zope.component.getUtility(
            icemac.ab.calendar.interfaces.IRecurringEvents)
        recurring_event = recurring_events[
            self.session['recurring-event-name']]
        date = self.session['recurred-event-date']
        data = icemac.ab.calendar.event.get_event_data_from_recurring_event(
            recurring_event, date)
        return data

    @z3c.form.button.buttonAndHandler(_('Apply'), name='add')
    def handleAdd(self, action):
        super(AddFromRecurredEvent, self).handleAdd(self, action)

    # Copy over the cancel button and handler:
    buttons += icemac.addressbook.browser.base.BaseAddForm.buttons.select(
        'cancel')
    handlers += icemac.addressbook.browser.base.BaseAddForm.handlers.copy()


class RecurredEventAbsoluteURL(zope.traversing.browser.AbsoluteURL,
                               icemac.ab.calendar.browser.base.View):
    """URL to customize a recurred event."""

    def __str__(self):
        return self.url(self.context.__parent__, 'customize-recurred-event',
                        event=self.context.recurring_event.__name__,
                        date=self.context.datetime.date().isoformat())

    __call__ = __str__
