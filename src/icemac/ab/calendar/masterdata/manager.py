# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import z3c.menu.ready2go
import z3c.menu.ready2go.manager
import zope.viewlet.manager


class ICalendarMasterData(z3c.menu.ready2go.ISiteMenu):
    """Containing viewlets which provide links to edit calendar master data."""


CalendarMasterDataManager = zope.viewlet.manager.ViewletManager(
    'calendar-master-data', ICalendarMasterData, bases=(
        z3c.menu.ready2go.manager.MenuManager,))
