# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
import unittest


class CategoryTests(unittest.TestCase):
    """Testing ..category.Category*."""

    def test_Category_implements_ICategory_interface(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICategory
        from icemac.ab.calendar.category import Category

        self.assertTrue(verifyObject(ICategory, Category()))

    def test_CategoryContainer_implements_ICategories_interface(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICategories
        from icemac.ab.calendar.category import CategoryContainer

        self.assertTrue(verifyObject(ICategories, CategoryContainer()))
