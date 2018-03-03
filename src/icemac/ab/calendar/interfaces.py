import zope.catalog.interfaces
from icemac.addressbook.i18n import _
from icemac.recurrence.interfaces import IRecurringDateTime
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


class ICalendarObject(zope.interface.Interface):
    """Marker interface for objects belonging to the calendar.

    This is needed to get the calendar skin layer.

    """


class ICalendar(ICalendarObject,
                zope.location.interfaces.ILocation):
    """Calender and storage for dates."""

    def get_events_for_month(month, timezone=None):
        """Get all events which belong to `month` sorted by datetime.

        All events = single events and recurred events in month but no deleted
        events.

        month ... ``gocept.month.Month`` object.
        timezone ... str, None defaults to UTC.

        """

    def get_events(start, end, timezone=None):
        """Get all events which between `start` and `end` sorted by datetime.

        `start` belongs to the interval but `end` does not.
        All events = single events and recurred events in month but no deleted
        events.

        start ... ``datetime.datetime`` object.
        end ... ``datetime.datetime`` object.
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
                              'external_persons', 'whole_day_event'):
                continue
            yield field

    def getToken(self, value):
        return icemac.addressbook.fieldsource.tokenize(
            self.event_entity, value.__name__)

    def getTitle(self, value):
        # If we get here it is no security risk to return the title because the
        # user is allowed to access the value. But we did not register class
        # types and security assertions for fields.
        return zope.security.proxy.removeSecurityProxy(value).title


event_fields_source = EventFieldsSource()


class ICalendarDisplaySettings(zope.interface.Interface):
    """Configuration of how to display the calendar."""

    event_additional_fields = zope.schema.List(
        title=_('Additional event fields to be displayed in calendar'),
        required=False,
        value_type=zope.schema.Choice(source=event_fields_source))

    person_keyword = zope.schema.Choice(
        title=_('Person keyword'),
        description=_(
            'Only persons having the keyword assigned which is selected here '
            'will show up in the person list when editing an event. '
            'If no keyword is selected all persons will show up.'),
        source=icemac.addressbook.interfaces.keyword_source,
        required=False)


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
    calendar_eventviews = zope.interface.Attribute(u'IEventViewContainer')


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
        site = zope.component.hooks.getSite()
        kw = ICalendarDisplaySettings(ICalendar(site)).person_keyword
        if kw is None:
            values = site.values()
        else:
            catalog = zope.component.getUtility(
                zope.catalog.interfaces.ICatalog)
            values = catalog.searchResults(keywords={'all_of': [kw.title]})
        return values

    def getTitle(self, value):
        return icemac.addressbook.interfaces.ITitle(value)


person_source = PersonSource()


class IBaseEvent(zope.interface.Interface):
    """Base of single, recurring and recurred events."""

    category = zope.schema.Choice(
        title=_('event category'), source=category_source)
    datetime = zope.schema.Datetime(title=_('datetime'), required=True)
    whole_day_event = zope.schema.Bool(
        title=_('whole day event?'), default=False)
    whole_day_event.setTaggedValue('omit-from-field-list', True)
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

    def listPersons():
        """Sorted list of all persons incl. external ones as strings."""

    def in_timezone(timezone):
        """Date of event normalized to `timezone`.

        Whole day events are counted as midnight.

        timezone ... str

        """


class IEvent(IBaseEvent):
    """A single event in the calendar."""

    deleted = zope.interface.Attribute(
        'Event has been deleted. Used to support deletion of recurred events.')


class IEventDateTime(zope.interface.Interface):
    """Datetime of an event, used for cataloging the event."""

    datetime = zope.interface.Attribute('datetime of the event')


class IRecurringEvents(ICalendarObject):
    """Container for recurring events."""

    def get_events(categories):
        """Return the events of categories sorted by priority (ascending).

        categories ... list of category titles or `[]` for all events
        """


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


class IRecurringEventAdditionalSchema(IRecurrence):
    """Additional schema fields for IRecurringEvent."""

    end = zope.schema.Date(title=_('recurrence end'), required=False)


class IRecurringEvent(IBaseEvent, IRecurringEventAdditionalSchema):
    """An event recurring after a defined period."""

    priority = zope.interface.Attribute(
        'Weight of the selected recurrence period.')

    def get_events(interval_start, interval_end, timezone):
        """Get the events computed from recurrence in the datetime interval."""


class IRecurredEvent(IBaseEvent):
    """An event computed from IRecurringEvent."""

    __parent__ = zope.interface.Attribute('Calendar the event belongs to')
    recurring_event = zope.interface.Attribute(
        'RecurringEvent which was the source for the RecurredEvent.')

    def create_from(recurring_event, datetime):
        """Create an instance with data from the recurring event but for ...

        ... `datetime`.
        """


class INoSecurityProxyType(zope.interface.interfaces.IInterface):
    """"Marker interface for interfaces which require security unwrapping.

    The `.masterdata.calendar.AnnotationField` security unrwarps contexts
    providing such an interface because they are stored in annotations.

    Usage: register the interface in ZCML via

    <interface interface=".your.Interface"
               type="icemac.ab.calendar.interfaces.INoSecurityProxyType" />
    """
