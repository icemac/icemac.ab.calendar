from .interfaces import ICalendarMasterData
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.manager
import zope.viewlet.manager


# Menu displaying the links to the edit the calendar master data
CalendarMasterDataManager = zope.viewlet.manager.ViewletManager(
    'calendar-master-data', ICalendarMasterData, bases=(
        z3c.menu.ready2go.manager.MenuManager,))


calendar_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'calendar-masterdata.html',
    icemac.ab.calendar.interfaces.ICategories,
    icemac.ab.calendar.interfaces.ICategory,
    icemac.ab.calendar.interfaces.IRecurringEvents,
    icemac.ab.calendar.interfaces.IRecurringEvent,
    'edit-display.html')
