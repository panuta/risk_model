import numbers

from django.http import Http404

from app.api.views import JsonListView, JsonDetailView
from app.risk.models import RiskModel, RiskModelField, RiskModelObject, RiskModelObjectValue, FieldType


def _validate_model_fields(data, errors, on_update=False):
    if not data.get('fields'):
        errors['fields'] = 'Fields is required'
    elif not isinstance(data.get('fields'), list):
        errors['fields'] = 'Fields must be a list'
    else:
        """
        Note: Trying to maintain order of submitted fields. So when client receive error messages,
        they will be able to match which field has error. Good for user experience.
        """
        validated_fields = []

        field_has_error = False
        fields_errors = []
        for field in data.get('fields'):
            validated_field = {}
            field_errors = {}

            # Field ID
            if field.get('field_id'):
                if not isinstance(field.get('field_id'), int):
                    field_has_error = True
                    field_errors['field_id'] = 'Field ID must be integer'
                else:
                    validated_field['field_id'] = field.get('field_id')

            # Name
            if not field.get('name'):
                field_has_error = True
                field_errors['name'] = 'Name must not be empty'
            elif not isinstance(field.get('name'), str):
                field_has_error = True
                field_errors['name'] = 'Name must be text'
            else:
                validated_field['name'] = field.get('name')

            # Slug
            if field.get('slug'):
                if not isinstance(field.get('slug'), str):
                    field_has_error = True
                    field_errors['slug'] = 'Slug must be text'
                else:
                    validated_field['slug'] = field.get('slug')

            # Type
            if not on_update:
                if not field.get('type'):
                    field_has_error = True
                    field_errors['type'] = 'Type must not be empty'
                elif field.get('type') not in FieldType.valid_choices():
                    field_has_error = True
                    field_errors['type'] = 'Type is invalid'
                elif field.get('type') == FieldType.ENUM and not field.get('choices'):
                    field_has_error = True
                    field_errors['choices'] = 'Missing choices data for enum type'
                else:
                    validated_field['type'] = field.get('type')

            if field.get('choices'):
                validated_field['choices'] = field.get('choices')

            if field.get('is_required'):
                if not isinstance(field.get('is_required'), bool):
                    field_has_error = True
                    field_errors['is_required'] = 'Slug must be boolean'
                else:
                    validated_field['is_required'] = field.get('is_required')

            validated_fields.append(validated_field)
            fields_errors.append(field_errors)

        if field_has_error:
            errors['fields'] = fields_errors

        return validated_fields, errors

    return None, errors


class RiskModelListView(JsonListView):
    model = RiskModel
    paginate_url_name = 'risk_api:model-list'

    def perform_create(self, request, validated_data, *args, **kwargs):
        risk_model = RiskModel.objects.create(name=validated_data['name'])

        for field in validated_data['fields']:
            RiskModelField.objects.create(risk_model=risk_model, **field)

        return risk_model

    def validate_on_create(self, request, data, *args, **kwargs):
        validated_data = {}
        errors = {}

        if not data.get('name'):
            errors['name'] = 'Name is required'
        else:
            validated_data['name'] = data.get('name')

        validated_fields, errors = _validate_model_fields(data, errors)
        if validated_fields:
            validated_data['fields'] = validated_fields

        return validated_data, errors


class RiskModelDetailView(JsonDetailView):
    model = RiskModel
    pk_url_kwarg = 'model_uuid'
    pk_field = 'uuid'

    def validate_on_update(self, request, data, *args, **kwargs):
        validated_data = {}
        errors = {}

        if not data.get('name'):
            errors['name'] = 'Name is required'
        else:
            validated_data['name'] = data.get('name')

        validated_fields, errors = _validate_model_fields(data, errors, True)
        if validated_fields:
            validated_data['fields'] = validated_fields

        return validated_data, errors

    def perform_update(self, request, validated_data, *args, **kwargs):
        model_uuid = kwargs.get(self.pk_url_kwarg)
        risk_model = RiskModel.objects.get(uuid=model_uuid)

        risk_model.name = validated_data.get('name')
        risk_model.save()

        # Updating model fields
        existing_fields = set(risk_model.fields.all())
        updated_fields = set()

        for field in validated_data.get('fields'):
            field_id = field.get('field_id')
            risk_model_field, _ = RiskModelField.objects.update_or_create(
                risk_model=risk_model, field_id=field_id, defaults=field)

            updated_fields.add(risk_model_field)

        # Remove fields
        deleting_fields = existing_fields - updated_fields
        RiskModelField.objects.filter(id__in=[f.id for f in deleting_fields]).delete()

        return risk_model

    def perform_delete(self, request, validated_data, *args, **kwargs):
        model_uuid = kwargs.get(self.pk_url_kwarg)
        risk_model = RiskModel.objects.get(uuid=model_uuid)
        risk_model.delete()


class RiskModelObjectListView(JsonListView):
    model = RiskModelObject
    paginate_url_name = 'risk_api:object-list'

    _risk_model = None
    _risk_model_fields = None

    # Cached values
    def _get_risk_model(self, uuid):
        if not self._risk_model:
            self._risk_model = RiskModel.objects.get(uuid=uuid)
        return self._risk_model

    # Cached values
    def _get_risk_model_fields(self, risk_model):
        if not self._risk_model_fields:
            self._risk_model_fields = RiskModelField.objects.filter(risk_model=risk_model)
        return self._risk_model_fields

    def validate_on_create(self, request, data, *args, **kwargs):
        risk_model = self._get_risk_object(uuid=kwargs.get('model_uuid'))
        risk_model_fields = self._get_risk_model_fields(risk_model=risk_model)

        validated_data = {}
        errors = {}

        for field in risk_model_fields:
            if field.is_required and not data.get(field.slug):
                errors[field.slug] = 'This field is required'
            elif data.get(field.slug):
                try:
                    if field.type == FieldType.ENUM:
                        validated_data[field.slug] = FieldType(field.type).to_valid_value(
                            data.get(field.slug), enum_choices=field.choices.split(','))
                    else:
                        validated_data[field.slug] = FieldType(field.type).to_valid_value(
                            data.get(field.slug))

                except ValueError:
                    errors[field.slug] = 'This field is invalid'

        return validated_data, errors

    def perform_create(self, request, validated_data, *args, **kwargs):
        risk_model = self._get_risk_object(uuid=kwargs.get('model_uuid'))
        risk_model_fields = self._get_risk_model_fields(risk_model=risk_model)

        risk_object = RiskModelObject.objects.create(risk_model=risk_model)
        for field in risk_model_fields:
            object_attrs = {
                'risk_object': risk_object,
                'field': field,
                'field_type': field.type,
                'value': validated_data.get(field.slug),
            }

            RiskModelObjectValue.objects.create(**object_attrs)

        return risk_object


class RiskModelObjectDetailView(JsonDetailView):
    model = RiskModelObject
    pk_url_kwarg = 'object_uuid'
    pk_field = 'uuid'

    _risk_object = None
    _risk_model_fields = None

    # Cached values
    def _get_risk_object(self, uuid):
        if not self._risk_object:
            self._risk_object = RiskModelObject.objects.get(uuid=uuid)
        return self._risk_object

    # Cached values
    def _get_risk_model_fields(self, risk_model):
        if not self._risk_model_fields:
            self._risk_model_fields = RiskModelField.objects.filter(risk_model=risk_model)
        return self._risk_model_fields

    def validate_on_update(self, request, data, *args, **kwargs):
        validated_data = {}
        errors = {}

        risk_object = self._get_risk_object(uuid=kwargs.get(self.pk_url_kwarg))
        risk_model_fields = self._get_risk_model_fields(risk_model=risk_object.risk_model)

        for field in risk_model_fields:
            if data.get(field.slug):
                try:
                    if field.type == FieldType.ENUM:
                        validated_data[field.slug] = FieldType(field.type).to_valid_value(
                            data.get(field.slug), enum_choices=field.choices.split(','))
                    else:
                        validated_data[field.slug] = FieldType(field.type).to_valid_value(
                            data.get(field.slug))

                except ValueError:
                    errors[field.slug] = 'This field is invalid'

        return validated_data, errors

    def perform_update(self, request, validated_data, *args, **kwargs):
        risk_object = self._get_risk_object(uuid=kwargs.get(self.pk_url_kwarg))
        risk_model_fields = self._get_risk_model_fields(risk_model=risk_object.risk_model)

        for field in risk_model_fields:
            if validated_data.get(field.slug):
                try:
                    object_value = RiskModelObjectValue.objects.get(risk_object=risk_object, field=field)
                except RiskModelObjectValue.DoesNotExist:
                    RiskModelObjectValue.objects.create(
                        risk_object=risk_object,
                        field=field,
                        field_type=field.type,
                        value=validated_data.get(field.slug))
                else:
                    object_value.value = validated_data.get(field.slug)
                    object_value.save()

        return risk_object

    def perform_delete(self, request, validated_data, *args, **kwargs):
        object_uuid = kwargs.get(self.pk_url_kwarg)
        risk_object = RiskModelObject.objects.get(uuid=object_uuid)
        risk_object.delete()
