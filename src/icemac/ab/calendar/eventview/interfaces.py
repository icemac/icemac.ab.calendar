from icemac.addressbook.i18n import _
import collections
import gocept.reference.field
import icemac.ab.calendar.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.sources
import zc.sourcefactory.basic
import zope.component
import zope.interface


class IEventViewContainer(zope.interface.Interface):
    """Container for event view configurations."""


class StartDateSource(icemac.addressbook.sources.TitleMappingSource):
    """Source mapping a relative number of days to a text."""

    _mapping = collections.OrderedDict((
        (-28, _('4 weeks in past')),
        (-21, _('3 weeks in past')),
        (-14, _('2 weeks in past')),
        (-7, _('1 week in past')),
        (-3, _('3 days in past')),
        (-1, _('1 day in past')),
        (0, _('current day')),
        (1, _('1 day in future')),
        (3, _('3 days in future')),
        (7, _('1 week in future')),
        (14, _('2 weeks in future')),
        (21, _('3 weeks in future')),
        (28, _('4 weeks in future')),
    ))


start_date_source = StartDateSource()


class DurationSource(icemac.addressbook.sources.TitleMappingSource):
    """Source a number of days to a text."""

    _mapping = collections.OrderedDict((
        (7, _('1 week')),
        (14, _('2 weeks')),
        (21, _('3 weeks')),
        (28, _('4 weeks')),
    ))


duration_source = DurationSource()


class IEventViewConfiguration(zope.interface.Interface):
    """Configuration of an view of events."""

    title = zope.schema.TextLine(
        title=_('title'),
        description=_('Shown on the event views page in the drop down.'))

    start = zope.schema.Choice(
        title=_('start date'),
        description=_(
            'The start date used in the view will be differing from the'
            ' current date by the chosen period of time.'),
        source=start_date_source,
    )

    duration = zope.schema.Choice(
        title=_('duration'),
        description=_('This number of days is shown in the view.'),
        source=duration_source,
    )

    categories = gocept.reference.field.Set(
        title=_('categories'),
        description=_(
            'Show in the view only events having one of these categories.'),
        required=False,
        value_type=zope.schema.Choice(
            title=_('event category'),
            source=icemac.ab.calendar.interfaces.category_source))

    fields = zope.schema.List(
        title=_('show fields'),
        description=_('Additional event fields to be shown in the view.'),
        required=False,
        value_type=zope.schema.Choice(
            source=icemac.ab.calendar.interfaces.event_fields_source))


class EventViewConfigurationSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Source containing all event view configurations."""

    def getValues(self):
        container = zope.component.getUtility(IEventViewContainer)
        return sorted(container.values(), key=lambda x: x.title)

    def getTitle(self, value):
        return icemac.addressbook.interfaces.ITitle(value)


class IEventViews(zope.interface.Interface):
    """Listing of event view configurations."""

    views = zope.schema.Choice(
        title=u'known views',
        source=EventViewConfigurationSource(),
    )


class IEventData(zope.interface.Interface):
    """Date of a single event which can be rendered in the event view."""

    datetime = zope.interface.Attribute('datetime.datetime object')

    whole_day = zope.interface.Attribute(
        'Event is the whole day, so do not display time.')

    title = zope.interface.Attribute(
        'Category resp. alternative title of the event.')

    fields = zope.interface.Attribute(
        'List of values of the fields selected in the event view config.')
