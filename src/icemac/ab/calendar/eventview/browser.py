from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.eventview.interfaces
import icemac.ab.calendar.masterdata.breadcrumb
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.table
import z3c.table.column


class RecurringEventsBreadCrumb(
        icemac.ab.calendar.masterdata.breadcrumb.CalendarMDChildBreadcrumb):
    """Breadcrumb for event views."""

    grok.adapts(
        icemac.ab.calendar.eventview.interfaces.IEventViewContainer,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Event views')


class Table(icemac.addressbook.browser.table.Table):
    """List event views."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW
    no_rows_message = _('No event views defined yet.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'title'),
        ]

    @property
    def values(self):
        return self.context.values()
