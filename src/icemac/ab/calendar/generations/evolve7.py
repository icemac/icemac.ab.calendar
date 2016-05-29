from icemac.ab.calendar.interfaces import ICalendarDisplaySettings, ICalendar
import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Set default value of `person_keyword` in CalendarDisplaySettings."""
    ICalendarDisplaySettings(ICalendar(addressbook)).person_keyword = None
