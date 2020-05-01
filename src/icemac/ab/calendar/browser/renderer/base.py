from io import StringIO
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.browser.renderer.interfaces
import icemac.addressbook.browser.interfaces
import zope.i18n


@grok.implementer(icemac.ab.calendar.browser.renderer.interfaces.IRenderer)
class Calendar(grok.MultiAdapter,
               icemac.ab.calendar.browser.base.View):
    """Base of calendar view."""

    grok.baseclass()
    grok.adapts(
        gocept.month.IMonth,
        icemac.addressbook.browser.interfaces.IAddressBookLayer,
        list)

    def __init__(self, month, request, events):
        self.request = request
        self.month = month
        self.events = events
        self._fd = StringIO()

    def write(self, string, *args, **kw):
        """Store a string which might contain % marks which get replaced."""
        text = string % args
        self._fd.write(text)
        if kw.pop('newline', True):
            self._fd.write(u'\n')

    def read(self):
        """Get the stored information back as unicode."""
        return self._fd.getvalue()

    def update(self):
        pass

    def render(self):
        raise NotImplementedError()

    def translate(self, message_id):
        return zope.i18n.translate(message_id, context=self.request)

    def __call__(self):
        self.update()
        return self.render()
