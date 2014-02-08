# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
import zope.interface


AUSFALL = 'ausfall'
INTERN = 'intern'


class IRenderer(zope.interface.Interface):
    """Renderer for a specific calendar view."""

    def __call__():
        """Return the rendered calendar."""


class UnknownLanguageError(LookupError):
    """Error indicating an unknown laguage."""


class IEventDescription(zope.interface.Interface):
    """Description of a single event which can be rendered."""

    context = zope.interface.Attribute('IEvent this description is based on.')

    kind = zope.interface.Attribute('event kind')
    datetime = zope.interface.Attribute('datetime.datetime object')
    prio = zope.interface.Attribute(
        'Event descriptions for the same `datetime` and `kind` with a higher '
        '`prio` override the ones with lower `prio`.')

    whole_day = zope.interface.Attribute(
        'Event is the whole day, so do not display time.')
    special_event = zope.interface.Attribute(
        'One of [AUSFALL, INTERN, None].')

    persons = zope.interface.Attribute(
        'Komma separated list of person names belonging to the event.')

    def getText(lang=None):
        """Textual description of the event.

        If `lang` is not `None` a hyphenation dict for this language is
        looked up. This might raise a `LookupError`. Otherwise the text is
        hyphenated for HTML.
        """

    def getInfo(lang=None):
        """List of additional information about the event.

        The contents of the list are defined in master data of calendar.

        """
