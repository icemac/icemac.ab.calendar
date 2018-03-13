from icemac.ab.calendar.interfaces import IEvent
from icemac.ab.calendar.interfaces import IRecurringEvent
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.item
import zope.interface


class CalendarMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Menu item for the calendar tab in the site menu."""


class CalendarMenuItemSelectedChecker(
        z3c.menu.ready2go.checker.TrueSelectedChecker,
        grok.MultiAdapter):
    """Selected checker for the calendar menu item in the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                CalendarMenuItem)

    CALENDAR_VIEW_NAMES = (
        'addEvent.html',
        'addFromRecurredEvent.html',
        'month.html',
        'year.html',
    )

    @property
    def selected(self):
        if IEvent.providedBy(self.context):
            return not(IRecurringEvent.providedBy(self.context))
        if self.view.__name__ in self.CALENDAR_VIEW_NAMES:
            return True
        return False
