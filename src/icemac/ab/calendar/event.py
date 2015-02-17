from datetime import datetime, time
from icemac.addressbook.i18n import _
import gocept.reference
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.entities
import icemac.addressbook.utils
import itertools
import persistent
import pytz
import zope.annotation.interfaces
import zope.container.btree
import zope.container.contained
import zope.interface


class BaseEvent(object):
    """Base class of all event classes."""

    def listPersons(self):
        """Sorted list of all persons incl. external ones as strings."""
        return sorted(itertools.chain(
            [icemac.addressbook.interfaces.IPersonName(x).get_name()
             for x in (self.persons or [])],
            (self.external_persons or [])))

    def in_timezone(self, timezone):
        """Date of event normalized to `timezone`.

        Whole day events are counted as midnight.

        """
        if self.whole_day_event:
            return timezone.localize(
                datetime.combine(self.date_without_time, time(0, 0)))
        return timezone.normalize(self.datetime)


class Event(persistent.Persistent,
            zope.container.contained.Contained,
            BaseEvent):
    """An event in the calendar."""

    zope.interface.implements(
        icemac.ab.calendar.interfaces.IEvent,
        zope.annotation.interfaces.IAttributeAnnotatable)
    zope.schema.fieldproperty.createFieldProperties(
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


class EventDateTime(grok.Adapter):
    """Catalog datetime of event."""

    grok.context(icemac.ab.calendar.interfaces.IEvent)
    grok.implements(icemac.ab.calendar.interfaces.IEventDateTime)

    @property
    def datetime(self):
        """Date of the event always having a time for indexing."""
        if self.context.whole_day_event:
            if self.context.date_without_time is not None:
                return datetime.combine(self.context.date_without_time,
                                        time(12, 0, tzinfo=pytz.utc))
            else:
                return None
        return self.context.datetime


class RecurringEventContainer(zope.container.btree.BTreeContainer):
    """A container for recurring events."""
    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurringEvents)

    def get_events(self):
        return sorted(self.values(), key=lambda x: x.priority)


class RecurringEvent(Event):
    """An event which repeats after a defined period."""
    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurringEvent)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurringEventAdditionalSchema)

    def get_events(self, interval_start, interval_end):
        """Get the events computed from recurrence in the interval."""
        if self.end is not None:
            end_datetime = self._get_end_datetime(interval_end.tzinfo)
            if end_datetime < interval_end:
                interval_end = end_datetime
        recurrence_dates = icemac.ab.calendar.recurrence.get_recurrences(
            self.datetime, self.period, interval_start, interval_end)
        for dt in recurrence_dates:
            yield RecurredEvent.create_from(self, dt)

    @property
    def priority(self):
        return icemac.ab.calendar.recurrence.get_recurring(
            self.datetime, self.period).weight

    def _get_end_datetime(self, timzone):
        return datetime.combine(self.end, time(23, 59, 59, tzinfo=timzone))


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


class RecurredEvent(BaseEvent):
    """An event computed from RecurringEvent."""

    zope.interface.implements(icemac.ab.calendar.interfaces.IRecurredEvent)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurredEvent)

    __parent__ = None
    recurring_event = None
    deleted = False

    @classmethod
    def create_from(cls, recurring_event, datetime):
        """Constructor: Copy data from recurring event."""
        field_names = zope.schema.getFieldNames(
            icemac.ab.calendar.interfaces.IEvent)
        data = {name: getattr(recurring_event, name) for name in field_names}
        data.update({
            'datetime': datetime,
            '__parent__': icemac.ab.calendar.interfaces.ICalendar(
                recurring_event),
            'recurring_event': recurring_event})

        return icemac.addressbook.utils.create_obj(cls, **data)
