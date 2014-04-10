# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 5


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.calendar.generations')
