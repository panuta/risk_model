from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from app.api.views import JsonListView
from app.risk.models import RiskModel, RiskModelField


# Remove CSRF definitely not best-practices but let's make it simple just for this challenge
@method_decorator(csrf_exempt, name='dispatch')
class RiskModelRESTView(JsonListView):
    model = RiskModel
    paginate_url_name = 'risk_api:model-list'

    def perform_create(self, request, validated_data, *args, **kwargs):
        risk_model = RiskModel.objects.create(name=validated_data['name'])

        for field in validated_data['fields']:
            RiskModelField.objects.create(risk_model=risk_model, **field)

        return risk_model

    def validate(self, data, errors):
        if not data.get('name', None):
            errors['name'] = 'Name must not be empty'

        if data.get('fields'):
            if not isinstance(data.get('fields'), list):
                errors['fields'] = 'Fields must be a list'
            else:
                fields_errors = []
                for field in data.get('fields'):
                    field_errors = {}
                    if not field.get('name', None):
                        field_errors['name'] = 'Name must not be empty'

                    if not field.get('type', None):
                        field_errors['type'] = 'Type must not be empty'

                    if field.get('type') not in ('text', 'number', 'datetime'):
                        field_errors['type'] = 'Type is invalid'

                    fields_errors.append(field_errors)

                errors['fields'] = fields_errors

        return data, errors
