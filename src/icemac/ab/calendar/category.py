from icemac.addressbook.i18n import _
import icemac.ab.calendar.interfaces
import icemac.addressbook.utils
import persistent
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.schema.fieldproperty


class CategoryContainer(zope.container.btree.BTreeContainer):
    """A container for calendar event categories."""

    zope.interface.implements(icemac.ab.calendar.interfaces.ICategories)


class Category(persistent.Persistent,
               zope.container.contained.Contained):
    """A category of an event."""

    zope.interface.implements(icemac.ab.calendar.interfaces.ICategory)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.ICategory)

    def __repr__(self):
        """Human readable representation of the object."""
        return '<Category title={0!r}>'.format(
            self.title.encode('ascii', 'replace'))


unique_titles = icemac.addressbook.utils.unique_by_attr_factory(
    'title', _(u'This category already exists.'))
