from .. testing import DateTimeClass
import datetime


def test_testing__DateTimeClass__format__1():
    """It formats a datetime to a date if forced to."""
    dt = datetime.datetime(2017, 1, 31, 13, 32)
    assert '17/01/31 13:32' == DateTimeClass().format(dt)
    assert '2017 1 31 ' == DateTimeClass().format(dt, force_date=True)
