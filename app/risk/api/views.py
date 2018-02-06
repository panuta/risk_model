from django.http import Http404

from app.api.views import JsonListView, JsonDetailView
from app.risk.models import RiskModel, RiskModelField


class RiskModelListView(JsonListView):
    model = RiskModel
    paginate_url_name = 'risk_api:model-list'

    def perform_create(self, request, validated_data, *args, **kwargs):
        risk_model = RiskModel.objects.create(name=validated_data['name'])

        for field in validated_data['fields']:
            RiskModelField.objects.create(risk_model=risk_model, **field)

        return risk_model

    def validate_on_create(self, request, data, errors):
        if not data.get('name', None):
            errors['name'] = 'Name must not be empty'

        if data.get('fields'):
            if not isinstance(data.get('fields'), list):
                errors['fields'] = 'Fields must be a list'
            else:
                """
                Note: Trying to maintain order of submitted fields. So when client receive error messages,
                they will be able to match which field has error. It's good for user experience.
                """
                has_error = False
                fields_errors = []
                for field in data.get('fields'):
                    field_errors = {}
                    if not field.get('name', None):
                        has_error = True
                        field_errors['name'] = 'Name must not be empty'

                    if not field.get('type', None):
                        has_error = True
                        field_errors['type'] = 'Type must not be empty'

                    if field.get('type') not in ('text', 'number', 'datetime'):
                        has_error = True
                        field_errors['type'] = 'Type is invalid'

                    fields_errors.append(field_errors)

                if has_error:
                    errors['fields'] = fields_errors

        return data, errors


class RiskModelDetailView(JsonDetailView):
    model = RiskModel
    pk_url_kwarg = 'model_uuid'
    pk_field = 'uuid'

    def perform_update(self, request, validated_data, *args, **kwargs):
        model_uuid = kwargs.get(self.pk_url_kwarg)

        try:
            risk_model = RiskModel.objects.get(uuid=model_uuid)
        except RiskModel.DoesNotExist:
            raise Http404('Risk model does not found')

        risk_model.name = validated_data.get('name')
        risk_model.save()

        # Updating model fields
        existing_fields = set(risk_model.fields.all())
        updated_fields = set()

        for field in validated_data.get('fields'):
            field_id = field.get('field_id', None)
            risk_model_field, _ = RiskModelField.objects.update_or_create(
                risk_model=risk_model, field_id=field_id, defaults=field)

            updated_fields.add(risk_model_field)

        deleting_fields = existing_fields - updated_fields
        RiskModelField.objects.filter(id__in=[f.id for f in deleting_fields]).delete()

        return risk_model

    def perform_delete(self, request, validated_data, *args, **kwargs):
        model_uuid = kwargs.get(self.pk_url_kwarg)

        try:
            risk_model = RiskModel.objects.get(uuid=model_uuid)
        except RiskModel.DoesNotExist:
            raise Http404('Risk model does not found')
        else:
            risk_model.delete()
