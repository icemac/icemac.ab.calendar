# -*- coding: utf-8 -*-
from icemac.ab.calendar.category import Category, CategoryContainer
from icemac.ab.calendar.interfaces import ICategory, ICategories
from zope.interface.verify import verifyObject
import zope.component.hooks


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


def test_category__changed__1(
        address_book, CategoryFactory, EventFactory, DateTime, browser):
    """It updates the `keywords` index if a category title was changed."""
    cat = CategoryFactory(address_book, u'foo')
    EventFactory(address_book, category=cat, alternative_title=u'event',
                 datetime=DateTime.now)

    event_titles = [
        x.alternative_title
        for x in address_book.calendar.get_events(
            DateTime.add(DateTime.now, days=-1),
            DateTime.add(DateTime.now, days=+1),
            categories=[u'foo'],
        )]
    assert ['event'] == event_titles

    browser.login('mgr')
    browser.open(browser.CALENDAR_CATEGORY_EDIT_URL)
    browser.getControl('event category').value = 'bar'
    browser.getControl('Apply').click()

    with zope.component.hooks.site(address_book):
        event_titles = [
            x.alternative_title
            for x in address_book.calendar.get_events(
                DateTime.add(DateTime.now, days=-1),
                DateTime.add(DateTime.now, days=+1),
                categories=['bar'],
            )]
    assert ['event'] == event_titles
