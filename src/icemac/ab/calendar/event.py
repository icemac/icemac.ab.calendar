from icemac.addressbook.i18n import _
import gocept.reference
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import persistent
import zope.annotation.interfaces
import zope.container.contained
import zope.interface


class Event(persistent.Persistent,
            zope.container.contained.Contained):
    "An event in the calendar."

    zope.interface.implements(
        icemac.ab.calendar.interfaces.IEvent,
        zope.annotation.interfaces.IAttributeAnnotatable)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.IEvent, omit=['category', 'persons'])

    category = gocept.reference.Reference('category', ensure_integrity=True)
    persons = gocept.reference.ReferenceCollection(
            'persons', ensure_integrity=True)

    def __init__(self):
        self.category = None  # prevent AttributeError on first read


@grok.adapter(icemac.ab.calendar.interfaces.IEvent)
@grok.implementer(icemac.addressbook.interfaces.ITitle)
def title(event):
    "Human readable title for an event."
    if event.alternative_title:
        return event.alternative_title
    if event.category:
        return icemac.addressbook.interfaces.ITitle(event.category)
    return _('event')
