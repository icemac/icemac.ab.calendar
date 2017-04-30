from ..install import update_calendar_infrastructure
import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Add recurring events infrastructure."""
    update_calendar_infrastructure(addressbook)
