import icemac.addressbook.generations.utils
import pytz


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Fix tzinfo for DST and convert it to UTC."""
    for event in addressbook.calendar.values():
        if event.datetime is None:
            continue
        if event.datetime.tzinfo == pytz.utc:
            continue
        # fix UTC offset in DST + convert to UTC
        event.datetime = pytz.utc.normalize(
            event.datetime.tzinfo.localize(
                event.datetime.replace(tzinfo=None)))
