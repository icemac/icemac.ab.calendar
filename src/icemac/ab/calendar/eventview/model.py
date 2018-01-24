import icemac.ab.calendar.eventview.interfaces
from icemac.addressbook.i18n import _
import icemac.ab.calendar.interfaces
import icemac.addressbook.utils
import persistent
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.schema.fieldproperty


@zope.interface.implementer(
    icemac.ab.calendar.eventview.interfaces.IEventViewContainer)
class EventViewContainer(zope.container.btree.BTreeContainer):
    """A container for event view configurations."""


@zope.interface.implementer(
    icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration)
class EventViewConfiguration(persistent.Persistent,
                             zope.container.contained.Contained):
    """A configuration of an view of events."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.ab.calendar.eventview.interfaces.IEventViewConfiguration)

    def __repr__(self):
        """Human readable representation of the object."""
        return u'<EventViewConfiguration title={0!r}>'.format(self.title)


unique_titles = icemac.addressbook.utils.unique_by_attr_factory(
    'title', _(u'This event view already exists.'))
