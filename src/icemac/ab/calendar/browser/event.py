from datetime import date, datetime, time
from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.browser.interfaces
import icemac.ab.calendar.event
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import icemac.addressbook.preferences.utils
import pytz
import z3c.form.button
import z3c.form.error
import z3c.form.form
import z3c.form.interfaces
import z3c.form.object
import z3c.form.term
import zope.component
import zope.traversing.browser


MIDNIGHT = time(0, 0)
NOON = time(12, 0)
EVENT_CONFIRMATION_FIELDS = (
    'category', 'alternative_title', 'whole_day_event', 'datetime')


def date_from_iso_string(string):
    """Convert an YYYY-MM-DD string to a python date object.

    Returns `None` if the string is `None`.

    """
    if string is None:
        return None
    return date(*tuple(int(x) for x in string.split('-')))


@zope.component.adapter(icemac.ab.calendar.interfaces.IEvent)
@zope.interface.implementer(
    icemac.ab.calendar.browser.interfaces.IEventDatetime)
class EventDatetime(object):
    """Adapter to edit an event using the IDatetime object field.

    Needs to be registered via ZCML, as grok has no model based security.
    """

    def __init__(self, context):
        self.context = self.__parent__ = context

    @property
    def datetime(self):
        return icemac.ab.calendar.browser.interfaces.IDatetime(self.context)

    @datetime.setter
    def datetime(self, value):
        self.context.datetime = value.datetime
        self.context.whole_day_event = value.whole_day_event


class Datetime(grok.Adapter):
    """Adapter storing the IDatetime field data and computing `datetime`."""

    grok.context(icemac.ab.calendar.interfaces.IEvent)
    grok.implements(icemac.ab.calendar.browser.interfaces.IDatetime)

    date = None
    time = None
    whole_day_event = None
    _datetime = None

    def __init__(self, context=None, whole_day_event=None):
        super(Datetime, self).__init__(context)
        self.whole_day_event = whole_day_event
        if isinstance(self.context, datetime):
            self._datetime = self.context
        elif self.context is not None:
            # context seems to be an IEvent
            self.__parent__ = context
            self._datetime = self.context.datetime
            self.whole_day_event = self.context.whole_day_event
        if self._datetime:
            local_datetime = self._timezone.normalize(self._datetime)
            self.date = local_datetime.date()
            self.time = local_datetime.time()

    @property
    def datetime(self):
        if self.whole_day_event:
            time = NOON
        else:
            time = self.time
        return pytz.utc.normalize(self._timezone.localize(
            datetime.combine(self.date, time)))

    @property
    def _timezone(self):
        return icemac.addressbook.preferences.utils.get_time_zone()


# Factory needed for the add form to initially store the IDatetime values:
z3c.form.object.registerFactoryAdapter(
    icemac.ab.calendar.browser.interfaces.IDatetime, Datetime)


class SourceFactoryMissingCollectionTermsSource(
        z3c.form.term.MissingCollectionTermsSource):
    """MissingCollectionTermsSource adapted to zc.sourcefactory.

    We need a zc.sourcefactory as base creating the `ITerms` adapter to
    be able to `_makeMissingTerm()` properly.
    """

    def _makeMissingTerm(self, value):
        term = self.terms.getTerm(value)
        term.title = _(u'Missing: ${value}', mapping=dict(value=term.title))
        return term


NoLongerAllowedPerson = z3c.form.error.ErrorViewMessage(
    _('Please deselect the persons prefixed with "Missing:" They are no '
      'longer in the list of available persons. (Maybe reconsider the '
      'following setting: Master Data > Calendar > Settings > '
      'Person keyword)'),
    error=zope.schema.interfaces.WrongContainedType,
    field=icemac.ab.calendar.interfaces.IBaseEvent['persons'])


class EventFields(object):
    """Form fields to add or edit an event."""

    interface = None

    @property
    def fields(self):
        fields = icemac.addressbook.interfaces.IEntity(self.interface)
        field_values = []
        for name, field in fields.getFields():
            if name == 'whole_day_event':
                continue
            elif name == 'datetime':
                field_values.append(
                    icemac.ab.calendar.browser.interfaces.IEventDatetime[
                        'datetime'])
            else:
                field_values.append(field)
        return z3c.form.field.Fields(*field_values)


class Add(EventFields, icemac.addressbook.browser.base.BaseAddForm):
    """Add form for an event."""

    title = _(u'Add new event')
    interface = icemac.ab.calendar.interfaces.IEvent
    class_ = icemac.ab.calendar.event.Event
    next_url = 'parent'
    ignoreContext = False

    def getContent(self):
        date = date_from_iso_string(self.request.get('date'))
        if date is not None:
            timezone = icemac.addressbook.preferences.utils.get_time_zone()
            selected_datetime = timezone.localize(datetime.combine(date, NOON))
            whole_day_event = True
        else:
            selected_datetime = None
            whole_day_event = False
        data = {'datetime': Datetime(selected_datetime, whole_day_event)}
        return data


class Edit(EventFields, icemac.addressbook.browser.base.GroupEditForm):
    """Edit for for an event."""

    title = _('Edit event')
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
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

    title = _('Delete event')
    label = _(u'Do you really want to delete this event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = EVENT_CONFIRMATION_FIELDS


class Clone(icemac.addressbook.browser.base.BaseCloneForm):
    """Clone event with confirmation."""

    title = _('Clone event')
    label = _(u'Do you really want to clone this event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = EVENT_CONFIRMATION_FIELDS


class CustomizeRecurredEvent(icemac.ab.calendar.browser.base.View):
    """Prepare customization of a RecurredEvent."""

    def __call__(self):
        self.session['recurring-event-name'] = self.request.form['event']
        self.session['recurred-event-date'] = date_from_iso_string(
            self.request.form['date'])
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
        timezone = icemac.addressbook.preferences.utils.get_time_zone()
        datetime = timezone.normalize(recurring_event.datetime)
        datetime = datetime.replace(
            year=date.year, month=date.month, day=date.day, tzinfo=None)
        # Fix possible DST offset:
        datetime = timezone.localize(datetime)
        data = icemac.ab.calendar.event.get_event_data_from_recurring_event(
            recurring_event, datetime)
        data['datetime'] = Datetime(
            data['datetime'], data.pop('whole_day_event'))
        return data


class AddFromRecurredEvent(icemac.ab.calendar.browser.base.View,
                           RecurredEventFormMixIn,
                           EventFields,
                           icemac.addressbook.browser.base.BaseAddForm):
    """Add form for changing a recurred event."""

    title = _(u'Edit recurred event')
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
                        EventFields,
                        icemac.addressbook.browser.base.BaseEditForm):
    """View form for a recurred event."""

    label = _(u'View recurred event')
    interface = icemac.ab.calendar.interfaces.IEvent
    mode = z3c.form.interfaces.DISPLAY_MODE
    next_url = 'parent'


class DeleteRecurredEvent(icemac.ab.calendar.browser.base.View,
                          RecurredEventFormMixIn,
                          EventFields,
                          icemac.addressbook.browser.base.BaseDeleteForm):
    """Add form for deleting a recurred event."""

    title = _('Delete recurred event')
    label = _(u'Do you really want to delete this recurred event?')
    interface = icemac.ab.calendar.interfaces.IEvent
    field_names = EVENT_CONFIRMATION_FIELDS
    next_url_after_delete = 'object'

    @property
    def status_title(self):
        content = self.getContent()
        if content['alternative_title']:
            return content['alternative_title']
        return icemac.addressbook.interfaces.ITitle(content['category'])

    def _do_delete(self):
        content = self.getContent()
        icemac.addressbook.utils.create_and_add(
            self.context, icemac.ab.calendar.event.Event,
            category=content['category'],
            datetime=content['datetime'].datetime,
            whole_day_event=content['datetime'].whole_day_event,
            deleted=True)


class RecurredEventAbsoluteURL(zope.traversing.browser.AbsoluteURL,
                               icemac.ab.calendar.browser.base.View):
    """URL to customize a recurred event."""

    def __str__(self):
        """URL of the recurrend event."""
        return self.url(self.context.__parent__, 'customize-recurred-event',
                        event=self.context.recurring_event.__name__,
                        date=self.context.datetime.date().isoformat())

    __call__ = __str__
