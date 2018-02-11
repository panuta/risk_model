import uuid
from enum import Enum

from django.db import models
from django.db.models import Q
from django_extensions.db.fields import AutoSlugField

from dateutil.parser import parse
from functools import reduce
from sequences import get_next_value

from app.api.models import SerializableMixin


# Risk models
# -------------------------------------

class RiskModel(SerializableMixin, models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name

    def to_dict(self):
        fields = [field.to_dict() for field in self.fields.all()]
        return {
            'uuid': self.uuid,
            'name': self.name,
            'fields': fields,
            'created': self.created,
        }


class FieldType(Enum):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    ENUM = 'enum'

    def __eq__(self, other):
        return self.value == other

    @classmethod
    def to_choices(cls):
        return ((str(value), name) for name, value in FieldType.__members__.items())

    @classmethod
    def valid_choices(cls):
        return [value.value for _, value in FieldType.__members__.items()]

    def to_valid_value(self, naive_value, enum_choices=None):
        if self == FieldType.TEXT:
            return str(naive_value)

        elif self == FieldType.NUMBER:
            return int(naive_value)

        elif self == FieldType.DATE:
            # Note: parse will throw ValueError if parsing error
            return parse(naive_value)

        elif self == FieldType.ENUM:
            enum_value = str(naive_value)
            if enum_value not in enum_choices:
                raise ValueError

            return enum_value

        return None


class RiskModelField(SerializableMixin, models.Model):
    risk_model = models.ForeignKey(RiskModel, related_name='fields', on_delete=models.CASCADE)
    field_id = models.PositiveIntegerField()
    slug = AutoSlugField(populate_from=['name'], editable=True, db_index=True)
    is_required = models.BooleanField(default=False)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, choices=FieldType.to_choices())
    choices = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('risk_model', 'slug')

    def __str__(self):
        return '{field_name} of {model_name}'.format(field_name=self.name, model_name=self.risk_model)

    def to_dict(self):
        ret = {
            'field_id': self.field_id,
            'slug': self.slug,
            'name': self.name,
            'type': self.type,
            'is_required': self.is_required,
        }

        if self.choices:
            ret['choices'] = self.choices

        return ret

    def save(self, **kwargs):
        if not self.field_id:
            self.field_id = get_next_value('risk_model_{}'.format(self.risk_model.id))
        super().save(**kwargs)


class RiskModelObject(SerializableMixin, models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    risk_model = models.ForeignKey(RiskModel, related_name='risk_objects', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return '{model_name} object #{uuid}'.format(model_name=self.risk_model, uuid=self.uuid)

    def to_dict(self):
        dict = {
            'uuid': self.uuid,
            'created': self.created,
        }
        for object_value in self.risk_values.all().select_related('field'):
            dict[object_value.field.slug] = object_value.value

        return dict


class RiskModelObjectValueManager(models.Manager):
    def filter(self, *args, **kwargs):
        new_args = list(args)

        attr_value = kwargs.pop('value', None)
        if attr_value:
            q_list = []

            # Text value
            str_value = str(attr_value)
            q_list.append({'value_text': str_value})

            # Number value
            try:
                number_value = int(attr_value)
            except:
                pass
            else:
                q_list.append({'value_number': number_value})

            # Date value
            try:
                date_value = parse(attr_value)
            except:
                pass
            else:
                q_list.append({'value_date': date_value})

            q = reduce(lambda x, y: x | y, [Q(**k) for k in q_list])
            new_args.append(q)

        args = new_args
        return super().filter(*args, **kwargs)


class RiskModelObjectValue(models.Model):
    risk_object = models.ForeignKey(RiskModelObject, related_name='risk_values', on_delete=models.CASCADE)
    field = models.ForeignKey(RiskModelField, on_delete=models.CASCADE)
    field_type = models.CharField(max_length=64, editable=False)  # Cached of `field.type`

    # Only one of these will be set as object value
    value_text = models.TextField(null=True, blank=True)
    value_number = models.IntegerField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_enum = models.CharField(max_length=128, null=True, blank=True)

    objects = RiskModelObjectValueManager()

    def __str__(self):
        return '{value} ({field})'.format(value=self.value, field=self.field)

    def _get_value(self):
        try:
            return getattr(self, 'value_{}'.format(self.field_type))
        except AttributeError:
            return None

    def _set_value(self, value):
        try:
            setattr(self, 'value_{}'.format(self.field_type), value)
        except AttributeError:
            pass

    value = property(_get_value, _set_value)
