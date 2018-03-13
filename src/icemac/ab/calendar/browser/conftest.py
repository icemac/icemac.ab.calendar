from icemac.ab.calendar.browser.calendar import EventDescription
import mock
import pytest


@pytest.fixture('session')
def EventDescriptionFactory(DateTime, zcmlS):
    """Create an EventDescription object."""
    def get_event_description(event, **kw):
        """Get an icemac.ab.calendar.browser.calendar.EventDescription.

        time_tuple ... `now` if empty.
        **kw ... attributes to be set on the event(!).
        """
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
