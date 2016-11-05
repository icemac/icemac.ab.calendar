import icemac.addressbook.generations.utils


ICalendar = 'icemac.ab.calendar.interfaces.ICalendar'


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Fix calendar start page to have a non-None view name."""
    if addressbook.startpage == (ICalendar, None):
        addressbook.startpage = (ICalendar, 'index.html')
