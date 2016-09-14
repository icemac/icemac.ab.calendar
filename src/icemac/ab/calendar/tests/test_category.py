# -*- coding: utf-8 -*-
from icemac.ab.calendar.category import Category, CategoryContainer
from icemac.ab.calendar.interfaces import ICategory, ICategories
from zope.interface.verify import verifyObject


def test_category__Category__1():
    """It implements the `ICategory` interface."""
    assert verifyObject(ICategory, Category())


def test_category__Category____repr____1():
    """It returns a readable representation."""
    category = Category()
    category.title = u'Füchschen'
    # repr() has to be ASCII, so everything else is replaced:
    assert "<Category title='F?chschen'>" == repr(category)


def test_category__CategoryContainer__1():
    """It implements the `ICategories` interface."""
    assert verifyObject(ICategories, CategoryContainer())
