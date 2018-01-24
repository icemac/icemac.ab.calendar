from icemac.addressbook.i18n import _
import collections
import icemac.addressbook.sources
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
        (-1, _('1 day in future')),
        (-3, _('3 days in future')),
        (-7, _('1 week in future')),
        (-14, _('2 weeks in future')),
        (-21, _('3 weeks in future')),
        (-28, _('4 weeks in future')),
    ))


start_date_source = StartDateSource()


class IEventViewConfiguration(zope.interface.Interface):
    """Configuration of an view of events."""

    title = zope.schema.TextLine(
        title=_('title'),
        description=_('Shown on the event views page in the drop down.'))

    start = zope.schema.Choice(
        title=_('start date'),
        description=_(
            'The actual start date is computed relative to current date,'
            ' when the view is rendered.'),
        source=start_date_source,
    )
