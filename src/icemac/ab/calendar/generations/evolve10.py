import icemac.addressbook.generations.utils
import zope.catalog
import zope.component


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Add event categories to `keywords` index."""
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    catalog.updateIndex(catalog['keywords'])
