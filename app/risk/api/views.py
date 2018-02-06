import json

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
