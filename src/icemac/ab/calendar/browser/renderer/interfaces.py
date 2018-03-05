import zope.interface


class IRenderer(zope.interface.Interface):
    """Renderer for a specific calendar view."""

    def __call__():
        """Return the rendered calendar."""


class UnknownLanguageError(LookupError):
    """Error indicating an unknown laguage."""
