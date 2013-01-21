# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import icemac.ab.calendar.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import persistent
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import icemac.addressbook.schema


class CategoryContainer(zope.container.btree.BTreeContainer):
    "A container for calendar event categories."
    zope.interface.implements(icemac.ab.calendar.interfaces.ICategories)


class Category(persistent.Persistent,
               zope.container.contained.Contained):
    "A category of an event."
    zope.interface.implements(icemac.ab.calendar.interfaces.ICategory)
    icemac.addressbook.schema.createFieldProperties(
        icemac.ab.calendar.interfaces.ICategory)


unique_titles = icemac.addressbook.utils.unique_by_attr_factory(
    'title', _(u'This category already exists.'))