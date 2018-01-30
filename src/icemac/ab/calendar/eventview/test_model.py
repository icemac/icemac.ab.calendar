# -*- coding: utf-8 -*-
from .interfaces import IEventViewConfiguration
from .interfaces import IEventViewContainer
from .model import EventViewConfiguration
from .model import EventViewContainer
from zope.interface.verify import verifyObject


def test_model__EventViewContainer__1():
    """It it fulfils the IEventViewContainer interface."""
    assert verifyObject(IEventViewContainer, EventViewContainer())


def test_model__EventViewConfiguration__1():
    """It it fulfils the IEventViewConfiguration interface."""
    assert verifyObject(IEventViewConfiguration, EventViewConfiguration())


def test_model__EventViewConfiguration____repr____1():
    """It has a human readable `repr` even if no title is set."""
    evc = EventViewConfiguration()
    evc.title = u'Have a 🧠!'
    assert isinstance(repr(evc), str)
    assert repr(evc) == "<EventViewConfiguration title=u'Have a \\U0001f9e0!'>"


def test_model__EventViewConfiguration____repr____2():
    """It has a human readable `repr` even if no title is set."""
    evc = EventViewConfiguration()
    assert repr(evc) == '<EventViewConfiguration title=None>'
