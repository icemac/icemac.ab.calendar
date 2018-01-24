from ..browser.event import EVENT_CONFIRMATION_FIELDS, EventFields
from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.masterdata.breadcrumb
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import icemac.recurrence
import z3c.table.column


class RecurringEventsBreadCrumb(
        icemac.ab.calendar.masterdata.breadcrumb.CalendarMDChildBreadcrumb):
    """Breadcrumb for recurring events."""

    grok.adapts(
        icemac.ab.calendar.interfaces.IRecurringEvents,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Recurring Events')


class RecurrenceColumn(z3c.table.column.I18nGetAttrColumn):
    """Column displaying the concrete recurrence of an event."""

    header = _('recurrence period')

    def getValue(self, item):
        recurring = icemac.recurrence.get_recurring(
            item.datetime, item.period)
        return recurring.info


class PersonsColumn(z3c.table.column.Column):
    """Column displaying all persons assigned to an event."""

    header = _('persons')

    def renderCell(self, item):
        return ', '.join(item.listPersons())


class StartColumn(z3c.table.column.GetAttrColumn):
    """Column which renders the start date.

    It localizes its datetime to selected timezone.
    It omits the time part of whole day events.
    """

    attrName = 'datetime'
    header = _('datetime')

    def getFormatter(self, obj):
        if obj.whole_day_event:
            category = 'date'
        else:
            category = 'dateTime'
        return self.request.locale.dates.getFormatter(
            category, 'short', None, u'gregorian')

    def getValue(self, obj):
        value = super(StartColumn, self).getValue(obj)
        if value and not obj.whole_day_event:
            value = value.astimezone(
                icemac.addressbook.preferences.utils.get_time_zone())
        return value

    def renderCell(self, obj):
        value = self.getValue(obj)
        if value:
            formatter = self.getFormatter(obj)
            value = formatter.format(value)
        return value


class Table(icemac.addressbook.browser.table.Table):
    """List recurring events."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW
    no_rows_message = _(u'No recurring events defined yet.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'title'),
            z3c.table.column.addColumn(
                self, StartColumn, 'datetime', weight=10),
            z3c.table.column.addColumn(
                self, RecurrenceColumn, 'period', weight=20),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.DateColumn, 'end',
                header=_('to'), entity=icemac.addressbook.interfaces.IEntity(
                    icemac.ab.calendar.interfaces.IRecurringEvent),
                field=icemac.ab.calendar.interfaces.IRecurringEvent['end'],
                weight=30),
            z3c.table.column.addColumn(
                self, PersonsColumn, 'persons', weight=40),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', header=_('notes'), attrName='text', weight=50),
        ]

    @property
    def values(self):
        return self.context.values()


class Add(EventFields, icemac.addressbook.browser.base.BaseAddForm):
    """Add form for a recurring event."""

    title = _(u'Add new recurring event')
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    class_ = icemac.ab.calendar.event.RecurringEvent
    next_url = 'parent'


class Edit(EventFields, icemac.addressbook.browser.base.GroupEditForm):
    """Edit form for recurring event."""

    title = _(u'Edit recurring event')
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    next_url = 'parent'
    z3c.form.form.extends(icemac.addressbook.browser.base.GroupEditForm,
                          ignoreFields=True)

    def applyChanges(self, data):
        # GroupForm has its own applyChanges but we need the one from
        # _AbstractEditForm here as inside the groups no changes are made but
        # there is a subscriber which raises an error which is handled by
        # _AbstractEditForm.
        return icemac.addressbook.browser.base._AbstractEditForm.applyChanges(
            self, data)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete',
        condition=icemac.addressbook.browser.base.can_access('@@delete.html'))
    def handleDelete(self, action):
        self.redirect_to_next_url('object', 'delete.html')


class Delete(icemac.addressbook.browser.base.BaseDeleteForm):
    """Confirm delete of recurring event."""

    title = _('Delete recurring event')
    label = _('Do you really want to delete this recurring event?')
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    field_names = EVENT_CONFIRMATION_FIELDS
