# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
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


class Edit(icemac.addressbook.browser.base.GroupEditForm):
    """Edit form for event category."""

    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    label = _(u'Edit event category')
    interface = icemac.ab.calendar.interfaces.ICategory
    next_url = 'parent'
    z3c.form.form.extends(icemac.addressbook.browser.base.GroupEditForm,
                          ignoreFields=True)
