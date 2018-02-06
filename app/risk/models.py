import uuid

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


class RiskModelField(SerializableMixin, models.Model):
    risk_model = models.ForeignKey(RiskModel, related_name='fields', on_delete=models.CASCADE)
    field_id = models.PositiveIntegerField()
    slug = AutoSlugField(populate_from=['name'], editable=True, db_index=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64)
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
    value_number = models.IntegerField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{value} ({field})'.format(value=self.get_value(), field=self.field)

    def get_value(self):
        if self.field_type == 'text':
            return self.value_text

        # TODO : add more type, convert to native data type

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
        if self.field_type == 'text':
            self.value_text = value

        # TODO : add more type

        return None
