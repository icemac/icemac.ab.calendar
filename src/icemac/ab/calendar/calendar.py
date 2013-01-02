# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import zope.container.btree
import zope.interface
import icemac.ab.calendar.interfaces


class Calendar(zope.container.btree.BTreeContainer):
    "Calendar containing dates."
    zope.interface.implements(icemac.ab.calendar.interfaces.ICalendar)

