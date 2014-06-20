# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import collections
import datetime
import gocept.reference.field
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import icemac.addressbook.sources
import zc.sourcefactory.basic
import zope.cachedescriptors.property
import zope.component
import zope.interface


PACKAGE_ID = 'icemac.ab.calendar'
DATE_INDEX = 'icemac.ab.calendar.event.date'


class ICalendar(zope.interface.Interface):
    """Calender and storage for dates."""

    def get_events(month, timezone=None):
        """Get all events which belong to `month` sorted by datetime.

        All events = single events and recurred events in month but no deleted
        events.

        month ... ``gocept.month.Month`` object.
        timezone ... str, None defaults to UTC.

        """


class EventFieldsSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Fields of an event for display in calendar view."""

    @property
    def event_entity(self):
        return icemac.addressbook.interfaces.IEntity(IEvent)

    def getValues(self):
        # We need the default and user defined fields but not the ones which
        # are always displayed or handeled in a specfic way:
        for field_name, field in self.event_entity.getRawFields():
            if field_name in ('datetime', 'category', 'alternative_title',
                              'external_persons'):
                continue
            yield field

    def getToken(self, value):
        return icemac.addressbook.fieldsource.tokenize(
            self.event_entity, value.__name__)

    def getTitle(self, value):
        return value.title

event_fields_source = EventFieldsSource()


class ICalendarDisplaySettings(zope.interface.Interface):
    """Configuration of how to display the calendar."""

    event_additional_fields = zope.schema.List(
        title=_('Additional event fields to be displayed in calendar'),
        required=False,
        value_type=zope.schema.Choice(source=event_fields_source))


class ICalendarProvider(zope.interface.Interface):
    """Marker interface for objects providing a calendar on an attribute.

    This is necessary to meet security which otherwise raises a ForbiddenError.

    """
    calendar = zope.interface.Attribute(u'ICalendar')


class ICalendarMasterData(zope.interface.Interface):
    """Marker interface for objects providing a calendar master data

    This is necessary to meet security which otherwise raises a ForbiddenError.

    """
    calendar_categories = zope.interface.Attribute(u'ICategories')
    calendar_recurring_events = zope.interface.Attribute(u'IRecurringEvents')


class ICategories(zope.interface.Interface):
    """Container for event categories."""


class ICategory(zope.interface.Interface):
    """An event category."""

    title = zope.schema.TextLine(title=_(u'event category'))


class CategorySource(zc.sourcefactory.basic.BasicSourceFactory):
    """Source of event categories defined for the calendar."""

    def getValues(self):
        categories = zope.component.getUtility(ICategories)
        return sorted(categories.values(), key=lambda x: x.title.lower())

    def getTitle(self, value):
        return value.title

category_source = CategorySource()


class PersonSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Persons in addressbook."""

    def getValues(self):
        return zope.site.hooks.getSite().values()

    def getTitle(self, value):
        return icemac.addressbook.interfaces.ITitle(value)

person_source = PersonSource()


class IBaseEvent(zope.interface.Interface):
    """Base of single, recurring and recurred events."""

    category = zope.schema.Choice(
        title=_('event category'), source=category_source)
    datetime = zope.schema.Datetime(title=_('datetime'))
    alternative_title = zope.schema.TextLine(
        title=_('alternative title to category'), required=False)
    persons = gocept.reference.field.Set(
        title=_('persons'), required=False,
        value_type=zope.schema.Choice(
            title=_('persons'), source=person_source))
    # Cannot use Set of TextLine here, as it is not supported by z3c.form:
    external_persons = zope.schema.List(
        title=_('other persons'), required=False,
        value_type=zope.schema.TextLine(title=_('person name')))
    text = zope.schema.Text(title=_('notes'), required=False)


class IEvent(IBaseEvent):
    """A single event in the calendar."""

    deleted = zope.interface.Attribute(
        'Event has been deleted. Used to support deletion of recurred events.')


class IEventDateTime(zope.interface.Interface):
    """Datetime of an event, used for cataloging the event."""

    datetime = zope.interface.Attribute('datetime of the event')


class IRecurringEvents(zope.interface.Interface):
    """Container for recurrign events."""


class RecurrencePeriodSource(icemac.addressbook.sources.TitleMappingSource):
    """Periods after which an event is repeated."""
    @zope.cachedescriptors.property.Lazy
    def _mapping(self):
        names_and_adapters = zope.component.getAdapters(
            [datetime.datetime.now()], IRecurringDateTime)
        return collections.OrderedDict(
            (name, adapter.title)
            for name, adapter in sorted(
                names_and_adapters, key=lambda x: x[1].weight))

recurrence_period_source = RecurrencePeriodSource()


class IRecurrence(zope.interface.Interface):
    """Time interval after which an event recurres."""

    period = zope.schema.Choice(
        title=_('recurrence period'), source=recurrence_period_source)


class IRecurringDateTime(zope.interface.Interface):
    """Recurring of a datetime.

    Period and base datetime are defined in class implementing the interface.

    """
    title = zope.interface.Attribute('Display title in RecurrencePeriodSource')
    weight = zope.interface.Attribute(
        'RecurrencePeriodSource uses `weight` to sort.')

    def __call__(interval_start, interval_end):
        """Iterable of recurrences of base datetime in the interval.

        interval_start, interval_end ... `datetime.date` objects

        """


class IRecurringEvent(IBaseEvent, IRecurrence):
    """An event recurring after a defined period."""

    def get_events(interval_start, interval_end):
        """Get the events computed from recurrence in the interval."""


class IRecurredEvent(IBaseEvent):
    """An event computed from IRecurringEvent."""

    __parent__ = zope.interface.Attribute('Calendar the event belongs to')
    recurring_event = zope.interface.Attribute(
        'RecurringEvent which was the source for the RecurredEvent.')

    def create_from(recurring_event, datetime):
        "Create an instance with data from recurring event but for `datetime`."
