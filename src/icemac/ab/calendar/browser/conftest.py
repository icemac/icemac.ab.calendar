from icemac.ab.calendar.browser.calendar import EventDescription
import mock
import pytest


@pytest.fixture('session')
def EventDescriptionFactory(DateTime):
    """Create an EventDescription object."""
    def get_event_description(time_tuple=(), event=None, **kw):
        """Get an icemac.ab.calendar.browser.calendar.EventDescription.

        time_tuple ... `now` if empty.
        **kw ... attributes to be set on the event(!).
        Does not actually create an event.

        """
        if event is None:
            event = mock.MagicMock()
        if time_tuple:
            event.datetime = DateTime(*time_tuple)
        else:
            event.datetime = DateTime.now
        for key, value in kw.items():
            setattr(event, key, value)
        ICalendarDisplaySettings = (
            'icemac.ab.calendar.interfaces.ICalendarDisplaySettings')
        get_time_zone_name = (
            'icemac.addressbook.preferences.utils.get_time_zone_name')
        with mock.patch(ICalendarDisplaySettings) as ICalendarDisplaySettings,\
                mock.patch('icemac.ab.calendar.interfaces.ICalendar'),\
                mock.patch(get_time_zone_name, return_value='UTC'):
            ICalendarDisplaySettings.event_additional_fields = ()
            return EventDescription(event)
    return get_event_description
