from icemac.addressbook.i18n import _
import collections
import datetime
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.masterdata.breadcrumb
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.datamanager
import icemac.addressbook.browser.metadata
import icemac.addressbook.metadata.interfaces
import z3c.form.field
import zope.component
import zope.dublincore.interfaces
import zope.schema.interfaces


class MasterData(object):
    """List of master data of the calendar."""


class CalendarMasterDataBreadCrumb(
        icemac.addressbook.browser.breadcrumb.MasterdataChildBreadcrumb):
    """Breadcrumb for calendar master data."""

    grok.adapts(
        MasterData,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Calendar')


class ModifierMetadataGroup(
        icemac.addressbook.browser.metadata.MetadataBaseGroup):
    """Group displaying only meta data information of modifier.

    To be used when creator is empty and creation date is irrelevant.
    """

    fields = z3c.form.field.Fields(
        icemac.addressbook.metadata.interfaces.IEditor).select('modifier')
    fields += z3c.form.field.Fields(
        zope.dublincore.interfaces.IDCTimes).select('modified')


class CalendarView(icemac.addressbook.browser.base.GroupEditForm):
    """Edit the calendar view settings."""

    groups = (ModifierMetadataGroup,)
    interface = icemac.ab.calendar.interfaces.ICalendarDisplaySettings
    next_url = 'parent'


class CalendarEditBreadCrumb(
        icemac.ab.calendar.masterdata.breadcrumb.CalendarMDChildBreadcrumb):
    """Breadcrumb for calendar master data edit view."""

    grok.adapts(
        CalendarView,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _(u'Edit settings')
    target_url = None


class AnnotationField(icemac.addressbook.browser.datamanager.AnnotationField,
                      grok.MultiAdapter):
    """Special AnnotationField for calendar."""

    grok.adapts(icemac.ab.calendar.interfaces.ICalendar,
                zope.schema.interfaces.IField)

    @property
    def no_security_proxy(self):
        interfaces = [x[1] for x in zope.component.getUtilitiesFor(
            icemac.ab.calendar.interfaces.INoSecurityProxyType)]
        return interfaces


class CalendarCounts(icemac.addressbook.browser.table.Table):
    """List calendar entries per year."""

    title = _('Counts of events per year')
    no_rows_message = _(u'No event events created in any year.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, z3c.table.column.GetItemColumn, 'type', idx='type',
                header=_(u'type')),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetItemColumn, 'year', idx='year',
                header=_(u'year')),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetItemColumn, 'count', idx='count',
                header=_(u'count'))
        ]

    @property
    def values(self):
        """The values are stored on the context."""
        MAX_DATETIME = datetime.datetime(2100, 12, 31, 23, 59, 59)
        events = self.context.query_single_events(
            icemac.ab.calendar.interfaces.MIN_SUPPORTED_DATETIME,
            MAX_DATETIME)

        events_by_year = collections.Counter([x.datetime.year for x in events])
        result = [{
            'type': _('event'),
            'year': year,
            'count': count}
            for year, count in sorted(events_by_year.items())]

        recurring_events = zope.component.getUtility(
            icemac.ab.calendar.interfaces.IRecurringEvents)
        count_recurring_events = len(recurring_events)
        if count_recurring_events:
            result.append({
                'type': _('recurring event'),
                'year': _('(all years)'),
                'count': len(recurring_events)})
        return result
