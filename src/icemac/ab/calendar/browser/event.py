from datetime import date
from icemac.addressbook.i18n import _
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.event
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import z3c.form.button
import z3c.form.form
import z3c.form.interfaces
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
        if icemac.addressbook.browser.base.can_access_uri_part(
                self.context, self.request, 'addFromRecurredEvent.html'):
            target_view = 'addFromRecurredEvent.html'
        else:
            target_view = 'viewRecurredEvent.html'
        self.request.response.redirect(self.url(self.context, target_view))
        return ''


class RecurredEventFormMixIn(object):
    """Mix-In providing data of recurred event from session."""

    def getContent(self):
        recurring_events = zope.component.getUtility(
            icemac.ab.calendar.interfaces.IRecurringEvents)
        recurring_event = recurring_events[
            self.session['recurring-event-name']]
        date = self.session['recurred-event-date']
        data = icemac.ab.calendar.event.get_event_data_from_recurring_event(
            recurring_event, date)
        return data


class AddFromRecurredEvent(icemac.ab.calendar.browser.base.View,
                           RecurredEventFormMixIn,
                           icemac.addressbook.browser.base.BaseAddForm):
    """Add form for changing a recurred event."""

    label = _(u'Edit recurred event')
    interface = icemac.ab.calendar.interfaces.IEvent
    class_ = icemac.ab.calendar.event.Event
    next_url = 'parent'
    ignoreContext = False
    buttons = z3c.form.button.Buttons()
    handlers = z3c.form.button.Handlers()

    # Rename `Add` button to `Apply`.
    @z3c.form.button.buttonAndHandler(_('Apply'), name='add')
    def handleAdd(self, action):
        super(AddFromRecurredEvent, self).handleAdd(self, action)

    @z3c.form.button.buttonAndHandler(_('Delete'), name='delete')
    def handleDelete(self, action):
        self.request.response.redirect(
            self.url(self.context, 'delete-recurred-event.html'))

    # Copy over the cancel button and handler:
    buttons += icemac.addressbook.browser.base.BaseAddForm.buttons.select(
        'cancel')
    handlers += icemac.addressbook.browser.base.BaseAddForm.handlers.copy()


class ViewRecurredEvent(icemac.ab.calendar.browser.base.View,
                        RecurredEventFormMixIn,
                        icemac.addressbook.browser.base.BaseEditForm):
    """View form for a recurred event."""

    label = _(u'View recurred event')
    interface = icemac.ab.calendar.interfaces.IEvent
    mode = z3c.form.interfaces.DISPLAY_MODE
    next_url = 'parent'


class DeleteRecurredEvent(icemac.ab.calendar.browser.base.View,
                          RecurredEventFormMixIn,
                          icemac.addressbook.browser.base.BaseDeleteForm):
    """Add form for deleting a recurred event."""

    label = _(u'Do you really want to delete this recurred event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = ('category', 'alternative_title', 'datetime')

    def _handle_action(self):
        content = self.getContent()
        icemac.addressbook.utils.create_and_add(
            self.context, icemac.ab.calendar.event.Event,
            category=content['category'], datetime=content['datetime'],
            deleted=True)
        title = content['alternative_title'] or content['category']
        self.status = _('"${title}" deleted.', mapping=dict(title=title))
        self.redirect_to_next_url('object')


class RecurredEventAbsoluteURL(zope.traversing.browser.AbsoluteURL,
                               icemac.ab.calendar.browser.base.View):
    """URL to customize a recurred event."""

    def __str__(self):
        return self.url(self.context.__parent__, 'customize-recurred-event',
                        event=self.context.recurring_event.__name__,
                        date=self.context.datetime.date().isoformat())

    __call__ = __str__
