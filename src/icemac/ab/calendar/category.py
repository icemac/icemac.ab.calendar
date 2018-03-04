from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.utils
import persistent
import zope.catalog.interfaces
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.schema.fieldproperty


@zope.interface.implementer(icemac.ab.calendar.interfaces.ICategories)
class CategoryContainer(zope.container.btree.BTreeContainer):
    """A container for calendar event categories."""


@zope.interface.implementer(icemac.ab.calendar.interfaces.ICategory)
class Category(persistent.Persistent,
               zope.container.contained.Contained):
    """A category of an event."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.interfaces.ICategory)

    def __repr__(self):
        """Human readable representation of the object."""
        return '<Category title={0!r}>'.format(
            self.title.encode('ascii', 'replace'))


unique_titles = icemac.addressbook.utils.unique_by_attr_factory(
    'title', _(u'This category already exists.'))


@grok.subscribe(icemac.ab.calendar.interfaces.ICategory,
                zope.lifecycleevent.IObjectModifiedEvent)
def changed(obj, event):
    """Update the catalog index if a category's title has changed."""
    # The notation of of this function is meant to have no code branches
    # because this cannot be easily tested and the other branches do not get
    # excecuted in real live.
    changed = [
        desc
        for desc in event.descriptions
        if (desc.interface == icemac.ab.calendar.interfaces.ICategory
            and 'title' in desc.attributes)]
    for x in changed:
        catalog = zope.component.getUtility(
            zope.catalog.interfaces.ICatalog)
        catalog.updateIndex(catalog.get('keywords'))
