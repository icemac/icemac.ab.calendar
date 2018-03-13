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


class IEventDescription(zope.interface.Interface):
    """Description of a single event which can be rendered in the calender."""

    context = zope.interface.Attribute('IEvent this description is based on.')

    datetime = zope.interface.Attribute('datetime.datetime object')
    prio = zope.interface.Attribute(
        'Event descriptions for the same `datetime` and `kind` with a higher '
        '`prio` override the ones with lower `prio`.')

    whole_day = zope.interface.Attribute(
        'Event is the whole day, so do not display time.')

    persons = zope.interface.Attribute(
        'Comma separated list of person names belonging to the event.')

    def getText(lang=None):
        """Textual description of the event.

        If `lang` is not `None` a hyphenation dict for this language is
        looked up. This might raise a `LookupError`. Otherwise the text is
        hyphenated for HTML.
        """

    def getInfo(lang=None):
        """List of additional information about the event.

        The contents of the list are defined in master data of calendar.

        """


class UnknownLanguageError(LookupError):
    """Error indicating an unknown laguage."""
