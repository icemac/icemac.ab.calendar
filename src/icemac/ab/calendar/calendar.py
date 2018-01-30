# -*- coding: utf-8 -*-
from .interfaces import DATE_INDEX
from datetime import datetime, time
import gocept.reference
import grokcore.annotation as grok
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.property
import icemac.addressbook.interfaces
import itertools
import pytz
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.interface


@zope.interface.implementer(icemac.ab.calendar.interfaces.ICalendar)
class Calendar(zope.container.btree.BTreeContainer):
    """Calendar containing dates."""

    def get_events(self, month, timezone=None):
        """Get all events which belong to `month`."""
        if timezone is None:
            timezone = pytz.utc
        else:
            timezone = pytz.timezone(timezone)
        midnight = time(0, 0, 0)
        start = timezone.localize(
            datetime.combine(month.firstOfMonth(), midnight))
        end = timezone.localize(
            datetime.combine((month + 1).firstOfMonth(), midnight))
        recurring_events = zope.component.getUtility(
            icemac.ab.calendar.interfaces.IRecurringEvents).get_events()
        recurred_events = [x.get_events(start, end, timezone)
                           for x in recurring_events]
        events_map = {(x.category, x.in_timezone(timezone)): x
                      for x in itertools.chain(*recurred_events)}
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        # The values for the index are: min, max, min_exclude, max_exclude
        single_events = catalog.searchResults(
            **{DATE_INDEX: {'between': (start, end, False, True)}})
        # Sort deleted events first. This way a recurred event can be deleted
        # and later on replaced by a new event of the same category.
        sorted_single_events = sorted(
            single_events, key=lambda x: int(x.deleted), reverse=True)
        # A single_event with the same category and datetime overwrites the
        # recurred event as it is its customization:
        single_events_map = {(x.category, x.in_timezone(timezone)): x
                             for x in sorted_single_events}
        events_map.update(single_events_map)
        # Filter out deleted recurred events and sort:
        return sorted(
            filter(lambda x: not x.deleted, events_map.values()),
            key=lambda x: (x.in_timezone(timezone),
                           icemac.addressbook.interfaces.ITitle(
                               x.category, None)))


class CalendarDisplaySettings(grok.Annotation):
    """Store calendar display settings in annotations."""

    grok.context(icemac.ab.calendar.interfaces.ICalendar)
    grok.implements(icemac.ab.calendar.interfaces.ICalendarDisplaySettings)

    person_keyword = gocept.reference.Reference(
        'person_keyword', ensure_integrity=True)
    event_additional_fields = icemac.ab.calendar.property.AddressBookField(
        '_event_additional_fields', multiple=True)

    def __init__(self, *args, **kw):
        super(CalendarDisplaySettings, self).__init__(*args, **kw)
        self.person_keyword = None


@grok.adapter(icemac.addressbook.interfaces.IAddressBook)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar(address_book):
    """Adapt the event to its calendar."""
    return address_book.calendar
