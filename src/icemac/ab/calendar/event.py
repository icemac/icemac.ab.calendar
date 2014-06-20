from icemac.addressbook.i18n import _
import gocept.reference
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.entities
import icemac.addressbook.utils
import persistent
import zope.annotation.interfaces
import zope.container.btree
import zope.container.contained
import zope.interface


class Event(persistent.Persistent,
            zope.container.contained.Contained):
    """An event in the calendar."""

    zope.interface.implements(
        icemac.ab.calendar.interfaces.IEvent,
        zope.annotation.interfaces.IAttributeAnnotatable)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.IEvent, omit=['category', 'persons'])

    category = gocept.reference.Reference('category', ensure_integrity=True)
    persons = gocept.reference.ReferenceCollection(
        'persons', ensure_integrity=True)
    deleted = False

    def __init__(self):
        # prevent AttributeErrors on first read
        self.category = None
        self.persons = None

event_entity = icemac.addressbook.entities.create_entity(
    _(u'event'), icemac.ab.calendar.interfaces.IEvent, Event)


@grok.adapter(icemac.ab.calendar.interfaces.IEvent)
@grok.implementer(icemac.addressbook.interfaces.ITitle)
def title(event):
    """Human readable title for an event."""
    if event.alternative_title:
        return event.alternative_title
    if event.category:
        return icemac.addressbook.interfaces.ITitle(event.category)
    return _('event')


@grok.adapter(icemac.ab.calendar.interfaces.IEvent)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar_of_IEvent(event):
    """Adapt the event to its calendar."""
    return event.__parent__


@grok.adapter(icemac.ab.calendar.interfaces.IRecurredEvent)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar_of_IRecurredEvent(event):
    """Adapt the event to its calendar."""
    return event.__parent__


@grok.adapter(icemac.ab.calendar.interfaces.IEvent)
@grok.implementer(icemac.ab.calendar.interfaces.IEventDateTime)
def event_datetime(event):
    """Catalog datetime of event."""
    return event


class RecurringEventContainer(zope.container.btree.BTreeContainer):
    """A container for recurring events."""
    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurringEvents)


class RecurringEvent(Event):
    """An event which repeats after a defined period."""
    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurringEvent)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurrence)

    def get_events(self, interval_start, interval_end):
        """Get the events computed from recurrence in the interval."""
        recurrence_dates = icemac.ab.calendar.recurrence.get_recurrences(
            self.datetime, self.period, interval_start, interval_end)
        for datetime in recurrence_dates:
            yield RecurredEvent.create_from(self, datetime)


recurring_event_entity = icemac.addressbook.entities.create_entity(
    _(u'recurring event'), icemac.ab.calendar.interfaces.IRecurringEvent,
    RecurringEvent)


def _get_field_name_on_IEvent(field, event_entity):
    """Get the name of the appropriate field on IEvent."""
    if not icemac.addressbook.interfaces.IField.providedBy(field):
        if field.__name__ in icemac.ab.calendar.interfaces.IBaseEvent:
            return field.__name__  # common field
        return None  # no-common field
    for name, recurring_field in event_entity.getRawFields(sorted=False):
        if (icemac.addressbook.interfaces.IField.providedBy(recurring_field)
                and field.title == recurring_field.title
                and field.type == recurring_field.type
                and field.values == recurring_field.values):
            return name
    return None


def get_event_data_from_recurring_event(recurring_event, date):
    """Get the event data from a recurring event

    This data can be written as the `__dict__` of the event.

    """
    event_entity = icemac.addressbook.interfaces.IEntity(
        icemac.ab.calendar.interfaces.IEvent)
    revent_entity = icemac.addressbook.interfaces.IEntity(
        icemac.ab.calendar.interfaces.IRecurringEvent)
    data = {}
    for name, field in revent_entity.getRawFields(sorted=False):
        key = _get_field_name_on_IEvent(field, event_entity)
        if key is not None:
            bound_field = icemac.addressbook.entities.get_bound_schema_field(
                recurring_event, revent_entity, field)
            data[key] = bound_field.get(bound_field.context)

    data[u'datetime'] = data[u'datetime'].replace(
        year=date.year, month=date.month, day=date.day)
    return data


@grok.adapter(icemac.ab.calendar.interfaces.IRecurringEvent)
@grok.implementer(icemac.ab.calendar.interfaces.IEventDateTime)
def recurring_event_datetime(event):
    """Do not catalog datetime of recurring event."""
    return None


@grok.adapter(icemac.ab.calendar.interfaces.IRecurringEvent)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar_of_recurring_event(recurring_event):
    """Adapt the recurring event to its calendar."""
    return icemac.ab.calendar.interfaces.ICalendar(
        icemac.addressbook.interfaces.IAddressBook(None))


class RecurredEvent(object):
    """An event computed from RecurringEvent."""

    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurredEvent)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurredEvent)

    __parent__ = None
    recurring_event = None
    deleted = False

    @classmethod
    def create_from(cls, recurring_event, datetime):
        """Constructor: Copy data from recurring event."""
        data = {name: getattr(recurring_event, name)
                for name in icemac.ab.calendar.interfaces.IEvent}
        data.update({
            'datetime': datetime,
            '__parent__': icemac.ab.calendar.interfaces.ICalendar(
                recurring_event),
            'recurring_event': recurring_event})

        return icemac.addressbook.utils.create_obj(cls, **data)
