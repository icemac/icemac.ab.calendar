# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from ..install import update_calendar_infrastructure
import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Update preferences to new structure."""
    update_calendar_infrastructure(addressbook)
