# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from .interfaces import DATE_INDEX
from datetime import datetime, time
import grokcore.annotation as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
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
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        if timezone is None:
            timezone = pytz.utc
        midnight = time(tzinfo=timezone)
        start = datetime.combine(month.firstOfMonth(), midnight)
        end = datetime.combine((month + 1).firstOfMonth(), midnight)
        # The values for the index are: min, max, min_exclude, max_exclude
        result_set = catalog.searchResults(
            **{DATE_INDEX: {'between': (start, end, False, True)}})
        return result_set


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
        for field in fields:
            values.append(icemac.addressbook.fieldsource.tokenize(
                icemac.addressbook.interfaces.IEntity(field.interface),
                field.__name__))
        self._event_additional_fields = values
