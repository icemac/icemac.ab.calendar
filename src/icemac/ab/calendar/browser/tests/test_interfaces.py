from icemac.ab.calendar.browser.interfaces import IDatetime
from mock import Mock
import datetime
import pytest
import zope.schema


@pytest.fixture('session')
def DatetimeFactory():
    """Factory to create a mock object implementing the IDatetime interface."""
    def create_datetime(date, time, whole_day_event):
        mock = Mock()
        mock.date = datetime.date(2015, 4, 15)
        if time:
            mock.time = datetime.time(18, 29)
        else:
            mock.time = None
        mock.whole_day_event = bool(whole_day_event)
        return mock
    return create_datetime


def test_interfaces__IDatetime__1(DatetimeFactory):
    """A whole day event with time is valid."""
    dt = DatetimeFactory('date', 'time', 'whole_day')
    assert [] == zope.schema.getValidationErrors(IDatetime, dt)


def test_interfaces__IDatetime__2(DatetimeFactory):
    """A whole day event without time is valid."""
    dt = DatetimeFactory('date', None, 'whole_day')
    assert [] == zope.schema.getValidationErrors(IDatetime, dt)


def test_interfaces__IDatetime__3(DatetimeFactory):
    """A non-whole day event with time is valid."""
    dt = DatetimeFactory('date', 'time', whole_day_event=False)
    assert [] == zope.schema.getValidationErrors(IDatetime, dt)


def test_interfaces__IDatetime__4(DatetimeFactory):
    """A non-whole day event without time is invalid."""
    dt = DatetimeFactory('date', None, whole_day_event=False)
    v = zope.schema.getValidationErrors(IDatetime, dt)
    assert 1 == len(v)
    assert 'Either enter a `time` or select `whole day event`!' == str(v[0][1])
