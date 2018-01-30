from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.eventview.interfaces
import icemac.ab.calendar.eventview.model
import icemac.ab.calendar.masterdata.breadcrumb
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import z3c.form.button
import z3c.form.form
import z3c.table.column


class RecurringEventsBreadCrumb(
        icemac.ab.calendar.masterdata.breadcrumb.CalendarMDChildBreadcrumb):
    """Breadcrumb for event views."""

    grok.adapts(
        icemac.ab.calendar.eventview.interfaces.IEventViewContainer,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Event views')


event_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    icemac.ab.calendar.eventview.interfaces.IEventViewContainer,
    icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration,
)


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


class Add(icemac.addressbook.browser.base.BaseAddForm):
    """Add form for an event view configuration."""

    title = _(u'Add new event view configuration')
    interface = icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration
    class_ = icemac.ab.calendar.eventview.model.EventViewConfiguration
    next_url = 'parent'


class Edit(icemac.addressbook.browser.base.GroupEditForm):
    """Edit form for event configuration."""

    title = _(u'Edit event view configuration')
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    interface = icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration
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
    """Confirm delete of event view configuration."""

    title = _('Delete event view configuration')
    label = _('Do you really want to delete this event view configuration?')
    interface = icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration
