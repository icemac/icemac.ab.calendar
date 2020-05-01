# -*- coding: utf-8 -*-
from .interfaces import IEventViewConfiguration
from .interfaces import IEventViewContainer
from .model import EventViewConfiguration
from .model import EventViewContainer
from zope.interface.verify import verifyObject
import six


def test_model__EventViewContainer__1():
    """It it fulfils the IEventViewContainer interface."""
    assert verifyObject(IEventViewContainer, EventViewContainer())


def test_model__EventViewConfiguration__1(zcmlS):
    """It it fulfils the IEventViewConfiguration interface."""
    assert verifyObject(IEventViewConfiguration, EventViewConfiguration())


def test_model__EventViewConfiguration____repr____1(zcmlS):
    """It has a human readable `repr` even if no title is set."""
    evc = EventViewConfiguration()
    evc.title = u'Have a 🧠!'
    assert isinstance(repr(evc), str)
    if six.PY2:  # pragma: PY2
        exp = "<EventViewConfiguration title=u'Have a \\U0001f9e0!'>"
    else:  # pragma: PY3
        exp = "<EventViewConfiguration title='Have a 🧠!'>"
    assert repr(evc) == exp


def test_model__EventViewConfiguration____repr____2():
    """It has a human readable `repr` even if no title is set."""
    evc = EventViewConfiguration()
    assert repr(evc) == '<EventViewConfiguration title=None>'
