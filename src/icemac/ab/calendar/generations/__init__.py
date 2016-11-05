import zope.generations.generations


GENERATION = 8


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.calendar.generations')
