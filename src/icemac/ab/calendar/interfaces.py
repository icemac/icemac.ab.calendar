# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import gocept.reference.field
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import zc.sourcefactory.basic
import zope.component
import zope.interface


DATE_INDEX = 'icemac.ab.calendar.event.date'


class ICalendar(zope.interface.Interface):
    """Calender and storage for dates."""

    def get_events(month, timezone=None):
        """Get all events which belong to `month`.

        month ... ``gocept.month.Month`` object.
        timezone ... ``pytz.timezone`` object, None defaults to UTC.
        """


class EventFieldsSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Fields of an event for display in calendar view."""

    def getValues(self):
        event_entity = icemac.addressbook.interfaces.IEntity(IEvent)
        # We need the default and user defined fields but not the ones which
        # are always displayed or handeled in a specfic way:
        for field_name, field in event_entity.getRawFields():
            if field_name in ('datetime', 'category', 'alternative_title',
                              'external_persons'):
                continue
            yield field

    def getToken(self, value):
        return icemac.addressbook.fieldsource.tokenize(
            icemac.addressbook.interfaces.IEntity(value.interface),
            value.__name__)

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


class IEvent(zope.interface.Interface):
    """A single event in the calendar."""

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
