# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from datetime import datetime, time
from .interfaces import DATE_INDEX
import icemac.ab.calendar.interfaces
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

