# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import z3c.table.column


class RecurrenceColumn(z3c.table.column.I18nGetAttrColumn):
    """Column displaying the concrete recurrence of an event."""

    def getValue(self, item):
        recurring = icemac.ab.calendar.recurrence.get_recurring(
            item.datetime, item.period)
        return recurring.info


class Table(icemac.addressbook.browser.table.Table):
    """List recurring events."""

    no_rows_message = _(u'No recurring events defined yet.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'title'),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrFormatterColumn, 'datetime',
                header=_('datetime'), attrName='datetime',
                formatterLength='short', weight=10),
            z3c.table.column.addColumn(
                self, RecurrenceColumn, 'period',
                header=_('recurrence period'), weight=20),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', header=_('notes'), attrName='text', weight=30),
        ]

    @property
    def values(self):
        return self.context.values()


class Add(icemac.addressbook.browser.base.BaseAddForm):
    """Add form for an recurring event."""

    label = _(u'Add new recurring event')
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    class_ = icemac.ab.calendar.event.RecurringEvent
    next_url = 'parent'


class Edit(icemac.addressbook.browser.base.GroupEditForm):
    """Edit form for recurring event."""

    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    label = _(u'Edit recurring event')
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    next_url = 'parent'
    z3c.form.form.extends(icemac.addressbook.browser.base.GroupEditForm,
                          ignoreFields=True)

    def applyChanges(self, data):
        # GroupForm has its own applyChanges but we need the one from
        # _AbstractEditForm here as inside the goups no changes are made but
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
    label = _(u'Do you really want to delete this recurring event?')
    interface = icemac.ab.calendar.interfaces.IRecurringEvent
    field_names = ('category', 'alternative_title', 'datetime')
