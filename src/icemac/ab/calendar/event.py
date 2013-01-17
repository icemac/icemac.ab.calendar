import gocept.reference
import icemac.ab.calendar.interfaces
import persistent
import zope.container.contained
import zope.interface


class Event(persistent.Persistent,
            zope.container.contained.Contained):
    "An event in the calendar."

    zope.interface.implements(icemac.ab.calendar.interfaces.IEvent)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.IEvent, omit=['category', 'persons'])

    category = gocept.reference.Reference('category', ensure_integrity=True)
    persons = gocept.reference.ReferenceCollection(
            'persons', ensure_integrity=True)
