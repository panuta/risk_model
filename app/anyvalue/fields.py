from hashlib import md5

from django.db import models

from app.anyvalue.enum import ValueType


def md5_hexdigest(value):
    return md5(value).hexdigest()


class AnyValue:
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value


class AnyValueTypeFieldInstance:
    def __init__(self, instance, field):
        self.content_type = None
        self.instance = instance
        self.field = field

    def get_value(self):
        value_type = getattr(self.instance, '{}_type'.format(self.field.name))

        if value_type == 'text':
            return getattr(self.instance, '{}_text'.format(self.field.name))

        # TODO : Add more types

        return None

    def set_value(self, value):
        value_type = getattr(self.instance, '{}_type'.format(self.field.name))
        setattr(self.instance, '{}_{}'.format(self.field.name, value_type), value)


class AnyValueField(models.Field):

    def contribute_to_class(self, cls, name, **kwargs):
        self.set_attributes_from_name(name)
        self.name = name
        self.key = md5_hexdigest(self.name.encode('utf-8'))
        self.field_names = {}

        type_field = models.CharField(max_length=64, editable=False)
        cls.add_to_class('{}_type'.format(self.name), type_field)

        value_text = models.TextField(null=True, blank=True)
        value_number = models.DecimalField(decimal_places=2, max_digits=30, null=True, blank=True)
        value_date = models.DateField(null=True, blank=True)
        value_enum = models.PositiveIntegerField(null=True, blank=True)  # Id to RiskModelEnumField object

        cls.add_to_class('{}_text'.format(self.name), value_text)
        cls.add_to_class('{}_number'.format(self.name), value_number)
        cls.add_to_class('{}_date'.format(self.name), value_date)
        cls.add_to_class('{}_enum'.format(self.name), value_enum)

        setattr(cls, name, self)

    def get_db_prep_save(self, value, connection):
        pass

    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError(self.get_db_prep_lookup)

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        return AnyValueTypeFieldInstance(instance, self)

    def __set__(self, instance, value):
        if isinstance(value, AnyValue):

            # TODO : Set enum

            setattr(instance, '{}_type'.format(self.name), value.value_type)
            setattr(instance, '{}_{}'.format(self.name, value.value_type), value.value)
        else:
            raise TypeError('{} value must be a AnyValue instance, not "{}"'.format(self.field.name, value))


class AnyValueTypeField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = ValueType.to_choices()
        kwargs['max_length'] = 64
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)

        def _get_amount(self, default=None):
            return getattr(self.instance, field_name, default)

        def _set_amount(self, value):
            return setattr(self.instance, field_name, value)

        cls.add_to_class('enum_choices', value_date)