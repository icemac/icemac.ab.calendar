# -*- coding: utf-8 -*-
from icemac.ab.calendar.browser.renderer.base import Calendar
from icemac.ab.calendar.browser.renderer.interfaces import IRenderer
from zope.interface.verify import verifyObject
import pytest


def test_base__Calendar__1():
    """It fulfills the `IRenderer` interface."""
    assert verifyObject(IRenderer, Calendar(None, None, None))


def test_base__Calendar__write__1():
    """It does not fail on non-ASCII chars."""
    calendar = Calendar(None, None, None)
    calendar.write(u'aäöü%s', u'ßen')
    assert u'aäöüßen\n' == calendar.read()


def test_base__Calendar__update__1():
    """It does nothing.

    Test is only here to complete test coverage.
    """
    calendar = Calendar(None, None, None)
    calendar.update()


def test_base__Calendar__render__1():
    """It raises an exception: method has to be implemented by child classes.

    Test is only here to complete test coverage.
    """
    calendar = Calendar(None, None, None)
    with pytest.raises(NotImplementedError):
        calendar.render()
