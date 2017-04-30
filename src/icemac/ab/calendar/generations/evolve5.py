import icemac.addressbook.generations.utils
import zope.component
import zope.catalog.interfaces
from ..interfaces import DATE_INDEX, IEventDateTime


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Do not catalog recurring events."""
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    index = catalog.get(DATE_INDEX)
    index.interface = IEventDateTime
