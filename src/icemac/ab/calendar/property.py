import icemac.ab.calendar.interfaces
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces


class AddressBookField(object):
    """Property which (de-)serializes a field object from/to a token.

    Caution: This class only works for fields on the event entity!
    """

    def __init__(self, attribute_name, multiple=False):
        self.multiple = multiple
        self.attrib = attribute_name

    def __get__(self, instance, class_):
        """Untokenize the stored value(s) to field objects."""
        if instance is None:
            return self
        values = []
        for token in getattr(instance, self.attrib, ()):
            try:
                field = icemac.addressbook.fieldsource.untokenize(token)[1]
            except KeyError:
                pass
            else:
                values.append(field)
        if self.multiple:
            return tuple(values)
        return values[0] if values else None

    def __set__(self, instance, value):
        """Store field objects as tokens."""
        if not self.multiple:
            value = [value] if value else []
        event_entity = icemac.addressbook.interfaces.IEntity(
            icemac.ab.calendar.interfaces.IEvent)
        tokens = [
            icemac.addressbook.fieldsource.tokenize(
                event_entity, field.__name__)
            for field in value]

        setattr(instance, self.attrib, tuple(tokens))
