from icemac.addressbook.i18n import _
import z3c.layer.pagelet
import zope.interface
import zope.schema


class ICalendarLayer(z3c.layer.pagelet.IPageletBrowserLayer):

    """Calendar browser layer."""


class IDatetime(zope.interface.Interface):

    """Object interface to edit datetime data."""

    whole_day_event = zope.schema.Bool(
        title=_('whole day event?'), default=False)
    date = zope.schema.Date(title=_('date'), required=True)
    time = zope.schema.Time(title=_('time'), required=False)
    datetime = zope.interface.Attribute(
        '`date` and `time` combined to a datetime.')

    @zope.interface.invariant
    def on_non_whole_day_event_time_must_be_set(event):
        if not event.whole_day_event and event.time is None:
            raise zope.interface.Invalid(
                _('Either enter a `time` or select `whole day event`!'))


class IEventDatetime(zope.interface.Interface):

    """Interface to edit event's date and time."""

    datetime = zope.schema.Object(title=_('datetime'), schema=IDatetime)
