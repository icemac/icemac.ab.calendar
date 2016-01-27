from icemac.ab.calendar.category import Category, CategoryContainer
from icemac.ab.calendar.interfaces import ICategory, ICategories
from zope.interface.verify import verifyObject


def test_category__Category__1():
    """It implements the `ICategory` interface."""
    assert verifyObject(ICategory, Category())


def test_category__CategoryContainer__1():
    """It implements the `ICategories` interface."""
    assert verifyObject(ICategories, CategoryContainer())
