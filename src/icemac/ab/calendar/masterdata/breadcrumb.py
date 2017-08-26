import grokcore.component as grok
import icemac.addressbook.browser.breadcrumb
import zope.component


class CalendarMDChildBreadcrumb(
        icemac.addressbook.browser.breadcrumb.Breadcrumb):
    """Base class for a breadcrumb those parent is calendar master data."""

    grok.baseclass()

    @property
    def parent(self):
        return zope.component.getMultiAdapter(
            (icemac.addressbook.interfaces.IAddressBook(self.context),
             self.request),
            name='calendar-masterdata.html')
