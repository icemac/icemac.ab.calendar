# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import gocept.reference.interfaces
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import z3c.table.column


class Table(icemac.addressbook.browser.table.Table):
    """List event categories."""

    no_rows_message = _(u'No event categories defined yet.')

    def setUpColumns(self):
        return [z3c.table.column.addColumn(
            self, icemac.addressbook.browser.table.TitleLinkColumn, 'title',
            header=_(u'event category')),
                ]

    @property
    def values(self):
        "The values are stored on the context."
        return self.context.values()


class Add(icemac.addressbook.browser.base.BaseAddForm):
    """Add form for event category."""

    label = _(u'Add new event category')
    interface = icemac.ab.calendar.interfaces.ICategory
    class_ = icemac.ab.calendar.category.Category
    next_url = 'parent'


def can_delete_category(form):
    """Button condition telling if the displayed category can be deleted."""
    return (
        icemac.addressbook.browser.base.can_access('@@delete.html')(form)
        and
        not gocept.reference.interfaces.IReferenceTarget(
            form.context).is_referenced()
        )


class Edit(icemac.addressbook.browser.base.GroupEditForm):
    """Edit form for event category."""

    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    label = _(u'Edit event category')
    interface = icemac.ab.calendar.interfaces.ICategory
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
        _(u'Delete'), name='delete', condition=can_delete_category)
    def handleDelete(self, action):
        self.redirect_to_next_url('object', '@@delete.html')


class Delete(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this event category?')
    interface = icemac.ab.calendar.interfaces.ICategory
    field_names = ('title', )
