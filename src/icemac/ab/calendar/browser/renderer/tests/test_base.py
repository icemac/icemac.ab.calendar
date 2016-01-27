# -*- coding: utf-8 -*-
from icemac.ab.calendar.browser.renderer.base import Calendar
from icemac.ab.calendar.browser.renderer.interfaces import IRenderer
from zope.interface.verify import verifyObject


def test_base__Calendar__1():
    """It fulfills the `IRenderer` interface."""
    assert verifyObject(IRenderer, Calendar(None, None, None))


def test_base__Calendar__write__1():
    """It does not fail on non-ASCII chars."""
    calendar = Calendar(None, None, None)
    calendar.write(u'aäöü%s', u'ßen')
    assert u'aäöüßen\n' == calendar.read()
