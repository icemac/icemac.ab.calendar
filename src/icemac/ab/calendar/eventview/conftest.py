from .model import EventViewConfiguration
import icemac.addressbook.utils
import pytest
import zope.component.hooks


@pytest.fixture(scope='session')
def EventViewConfigurationFactory():
    """Create an event view configuration in its container."""
    def create_eventview_configuration(address_book, title, **kw):
        parent = address_book.calendar_eventviews
        with zope.component.hooks.site(address_book):
            name = icemac.addressbook.utils.create_and_add(
                parent, EventViewConfiguration, title=title, **kw)
        return parent[name]
    return create_eventview_configuration
