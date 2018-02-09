import uuid
from enum import Enum

from django.db import models
from django_extensions.db.fields import AutoSlugField

from dateutil.parser import parse
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


class FieldTypeMeta(type):
    def __contains__(cls, item):
        print('CONTAIN: {}'.format(item))
        return True


class FieldType(Enum, metaclass=FieldTypeMeta):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    ENUM = 'enum'

    @classmethod
    def to_choices(cls):
        return ((str(value), name) for name, value in FieldType.__members__.items())

    @classmethod
    def to_value(cls, field_type, naive_value):
        if field_type == 'text':
            return str(naive_value)
        elif field_type == 'number':
            return int(naive_value)
        elif field_type == 'date':
            return parse(naive_value)
        elif field_type == 'enum':
            return int(naive_value)
        return None


class RiskModelField(SerializableMixin, models.Model):
    risk_model = models.ForeignKey(RiskModel, related_name='fields', on_delete=models.CASCADE)
    field_id = models.PositiveIntegerField()
    slug = AutoSlugField(populate_from=['name'], editable=True, db_index=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, choices=FieldType.to_choices())
    is_required = models.BooleanField(default=False)

    class Meta:
        unique_together = ('risk_model', 'slug')

    def __str__(self):
        return '{field_name} of {model_name}'.format(field_name=self.name, model_name=self.risk_model)

    def to_dict(self):
        return {
            'field_id': self.field_id,
            'slug': self.slug,
            'name': self.name,
            'type': self.type,
            'is_required': self.is_required,
        }

    def save(self, **kwargs):
        if not self.field_id:
            self.field_id = get_next_value('risk_model_{}'.format(self.risk_model.id))
        super().save(**kwargs)


class RiskModelEnumField(models.Model):
    field = models.ForeignKey(RiskModelField, on_delete=models.CASCADE)
    value = models.CharField(max_length=128)

    class Meta:
        unique_together = ('field', 'value')

    def __str__(self):
        return self.value


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
            dict[object_value.field.slug] = object_value.get_value()

        return dict


class RiskModelObjectValue(models.Model):
    risk_object = models.ForeignKey(RiskModelObject, related_name='risk_values', on_delete=models.CASCADE)
    field = models.ForeignKey(RiskModelField, on_delete=models.CASCADE)
    field_type = models.CharField(max_length=64, editable=False)  # Same as `type` in `field.type`

    # Only one of these will be set as object value
    value_text = models.TextField(null=True, blank=True)
    value_number = models.DecimalField(decimal_places=2, max_digits=30, null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_enum = models.PositiveIntegerField(null=True, blank=True)  # Id to RiskModelEnumField object

    def __str__(self):
        return '{value} ({field})'.format(value=self.get_value(), field=self.field)

    def get_value(self):
        try:
            return getattr(self, 'value_{}'.format(self.field_type))
        except AttributeError:
            return None

    @classmethod
    def to_value(cls, field_type, naive_value):



        if field_type == 'text':
            return str(naive_value)
        elif field_type == 'number':
            return int(naive_value)
        elif field_type == 'datetime':
            return parse(naive_value)
        return None

    def set_value(self, value):
        try:
            setattr(self, 'value_{}'.format(self.field_type), value)
        except AttributeError:
            pass
