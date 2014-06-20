# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from .interfaces import DATE_INDEX
from datetime import datetime, time
import grokcore.annotation as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import itertools
import pytz
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.interface


class Calendar(zope.container.btree.BTreeContainer):
    "Calendar containing dates."
    zope.interface.implements(icemac.ab.calendar.interfaces.ICalendar)

    def get_events(self, month, timezone=None):
        """Get all events which belong to `month`."""
        if timezone is None:
            timezone = 'utc'
        midnight = time(tzinfo=pytz.timezone(timezone))
        start = datetime.combine(month.firstOfMonth(), midnight)
        end = datetime.combine((month + 1).firstOfMonth(), midnight)

        recurring_events = zope.component.getUtility(
            icemac.ab.calendar.interfaces.IRecurringEvents).values()
        recurred_events = [x.get_events(start, end) for x in recurring_events]
        events_map = {(x.category, x.datetime): x
                      for x in itertools.chain(*recurred_events)}

        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        # The values for the index are: min, max, min_exclude, max_exclude
        single_events = catalog.searchResults(
            **{DATE_INDEX: {'between': (start, end, False, True)}})
        # A single_event with the same category and datetime overwrites the
        # recurred event as it is its customization:
        events_map.update({(x.category, x.datetime): x
                           for x in single_events})
        # Filter out deleted recurred events and sort:
        return sorted(filter(lambda x: not x.deleted, events_map.values()),
                      key=lambda x: x.datetime)


class CalendarDisplaySettings(grok.Annotation):
    """Store calendar display settings in annotations."""
    grok.context(icemac.ab.calendar.interfaces.ICalendar)
    grok.implements(icemac.ab.calendar.interfaces.ICalendarDisplaySettings)

    _event_additional_fields = []

    @property
    def event_additional_fields(self):
        return [icemac.addressbook.fieldsource.untokenize(value)[1]
                for value in self._event_additional_fields]

    @event_additional_fields.setter
    def event_additional_fields(self, fields):
        values = []
        event_entity = icemac.addressbook.interfaces.IEntity(
            icemac.ab.calendar.interfaces.IEvent)
        for field in fields:
            values.append(icemac.addressbook.fieldsource.tokenize(
                event_entity, field.__name__))
        self._event_additional_fields = values


@grok.adapter(icemac.addressbook.interfaces.IAddressBook)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar(address_book):
    "Adapt the event to its calendar."
    return address_book.calendar
