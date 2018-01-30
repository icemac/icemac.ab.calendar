from ..property import AddressBookField
import icemac.addressbook.addressbook


class ExampleSingle(object):
    """Example storing single values."""

    foo = AddressBookField('_storage')


class ExampleMultiple(object):
    """Example storing multiple values."""

    foo = AddressBookField('_storage', multiple=True)


def test_property__AddressBookField____get____1():
    """It returns itself on the class."""
    assert isinstance(ExampleSingle.foo, AddressBookField)


def test_property__AddressBookField____get____2():
    """It returns an empty tuple for multiple if no value got set."""
    assert () == ExampleMultiple().foo


def test_property__AddressBookField____get____3():
    """It returns `None` for single if no value got set."""
    assert ExampleSingle().foo is None


def test_property__AddressBookField____get____4(address_book):
    """It returns field objects for multiple values."""
    ex = ExampleMultiple()
    ex._storage = ('IcemacAbCalendarEventEvent###persons',
                   'IcemacAbCalendarEventEvent###category')
    assert (
        icemac.ab.calendar.event.event_entity.getRawField('persons'),
        icemac.ab.calendar.event.event_entity.getRawField('category'),
    ) == ex.foo


def test_property__AddressBookField____get____5(address_book):
    """It returns a single field object for a single value."""
    ex = ExampleSingle()
    ex._storage = ('IcemacAbCalendarEventEvent###persons', )
    assert (
        icemac.ab.calendar.event.event_entity.getRawField('persons') == ex.foo)


def test_property__AddressBookField____set____1(address_book):
    """It stores multiple values in a tuple on the instance."""
    ex = ExampleMultiple()
    ex.foo = [
        icemac.ab.calendar.event.event_entity.getRawField('persons'),
        icemac.ab.calendar.event.event_entity.getRawField('category'),
    ]
    assert ('IcemacAbCalendarEventEvent###persons',
            'IcemacAbCalendarEventEvent###category') == ex._storage


def test_property__AddressBookField____set____2(address_book):
    """It stores single values in a tuple on the instance."""
    ex = ExampleSingle()
    ex.foo = icemac.ab.calendar.event.event_entity.getRawField('category')
    assert ('IcemacAbCalendarEventEvent###category', ) == ex._storage


def test_property__AddressBookField____set____3(address_book):
    """It is able to set a single value to `None`."""
    ex = ExampleSingle()
    ex.foo = None
    assert () == ex._storage


def test_property__AddressBookField____get______set____1(address_book):
    """Get after set returns the values which were set. ."""
    ex = ExampleMultiple()
    value = (
        icemac.ab.calendar.event.event_entity.getRawField('persons'),
        icemac.ab.calendar.event.event_entity.getRawField('category'),
    )
    ex.foo = value
    assert value == ex.foo
