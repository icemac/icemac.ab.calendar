from datetime import datetime, time
from icemac.addressbook.i18n import _
from icemac.addressbook.interfaces import IField
import gocept.reference
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import icemac.recurrence
import itertools
import persistent
import pytz
import zope.annotation.interfaces
import zope.container.btree
import zope.container.contained
import zope.interface


MIDNIGHT = time(0, 0)
NOON = time(12, 0)


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
                datetime.combine(self.datetime.date(), MIDNIGHT))
        return timezone.normalize(self.datetime)


event_schema = icemac.ab.calendar.interfaces.IEvent


@zope.interface.implementer(
    event_schema,
    icemac.addressbook.interfaces.ISchemaProvider,
    zope.annotation.interfaces.IAttributeAnnotatable)
class Event(persistent.Persistent,
            zope.container.contained.Contained,
            BaseEvent):
    """An event in the calendar."""

    schema = event_schema

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

    def __repr__(self):
        """Custom repr to look inside the event for debugging purposes."""
        fstr = (
            "<{0.__class__.__name__}"
            " datetime='{0.datetime}'"
            " title={1!r},"
            " deleted={0.deleted}>"
        )
        return fstr.format(
            self, icemac.addressbook.interfaces.ITitle(self, '<unknown>'))


event_entity = icemac.addressbook.entities.create_entity(
    _(u'event'), icemac.ab.calendar.interfaces.IEvent, Event)


@grok.adapter(icemac.ab.calendar.interfaces.IEvent)
@grok.implementer(icemac.addressbook.interfaces.ITitle)
def event_title(event):
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
        if self.context.datetime is None:
            return None
        if self.context.whole_day_event:
            return pytz.utc.localize(
                datetime.combine(self.context.datetime.date(), NOON))
        return self.context.datetime


@zope.interface.implementer(icemac.ab.calendar.interfaces.IRecurringEvents)
class RecurringEventContainer(zope.container.btree.BTreeContainer):
    """A container for recurring events."""

    def get_events(self, categories):
        events = self.values()
        if categories:
            events = [x for x in events if x.category.title in categories]
        return sorted(events, key=lambda x: x.priority)


recurring_event_schema = icemac.ab.calendar.interfaces.IRecurringEvent


@zope.interface.implementer(recurring_event_schema)
class RecurringEvent(Event):
    """An event which repeats after a defined period."""

    schema = recurring_event_schema
    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurringEventAdditionalSchema)

    def get_events(self, interval_start, interval_end, timezone):
        """Get the events computed from recurrence in the interval."""
        if self.end is not None:
            end_datetime = self._get_end_datetime(interval_end.tzinfo)
            if end_datetime < interval_end:
                interval_end = end_datetime
        recurrence_dates = icemac.recurrence.get_recurrences(
            timezone.normalize(self.datetime), self.period,
            interval_start, interval_end)
        for dt in recurrence_dates:
            yield RecurredEvent.create_from(self, dt)

    @property
    def priority(self):
        return icemac.recurrence.get_recurring(
            self.datetime, self.period).weight

    def _get_end_datetime(self, timzone):
        return datetime.combine(self.end, time(23, 59, 59, tzinfo=timzone))


recurring_event_entity = icemac.addressbook.entities.create_entity(
    _(u'recurring event'), icemac.ab.calendar.interfaces.IRecurringEvent,
    RecurringEvent)


def _get_field_name_on_IEvent(field, event_entity):
    """Get the name of the appropriate field on IEvent."""
    if not IField.providedBy(field):
        if field.__name__ in icemac.ab.calendar.interfaces.IBaseEvent:
            return field.__name__  # common field
        return None  # no-common field
    for name, recurring_field in event_entity.getRawFields(sorted=False):
        if (IField.providedBy(recurring_field) and
                field.title == recurring_field.title and
                field.type == recurring_field.type and
                field.values == recurring_field.values):
            return name
    return None


def get_event_data_from_recurring_event(recurring_event, datetime):
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
    data[u'datetime'] = datetime
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


@zope.interface.implementer(
    icemac.ab.calendar.interfaces.IRecurredEvent,
    icemac.addressbook.interfaces.IUserFieldStorage)
class RecurredEvent(BaseEvent):
    """An event computed from RecurringEvent."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.IRecurredEvent)

    __parent__ = None
    recurring_event = None
    deleted = False

    @classmethod
    def create_from(cls, recurring_event, datetime):
        """Constructor: Copy data from recurring event."""
        data = get_event_data_from_recurring_event(recurring_event, datetime)
        data.update({
            '__parent__': icemac.ab.calendar.interfaces.ICalendar(
                recurring_event),
            'recurring_event': recurring_event})

        return icemac.addressbook.utils.create_obj(cls, **data)

    def __repr__(self):
        """Custom repr to look inside the recurred event to debug it."""
        return "<RecurredEvent datetime='{0.datetime}' title={1!r}>".format(
            self, icemac.addressbook.interfaces.ITitle(self, '<unknown>'))


@grok.adapter(icemac.ab.calendar.interfaces.IRecurredEvent)
@grok.implementer(icemac.addressbook.interfaces.ITitle)
def recurred_event_title(event):
    return event_title(event)


@grok.implementer(icemac.addressbook.interfaces.IKeywordTitles)
class EventKeywords(grok.Adapter):
    """Event categories to be stored in the `keywords` index in the catalog."""

    grok.context(icemac.ab.calendar.interfaces.IBaseEvent)

    def __init__(self, context):
        self.context = context

    def get_titles(self):
        return [icemac.addressbook.interfaces.ITitle(self.context.category)]
