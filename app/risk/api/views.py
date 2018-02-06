from app.api.views import JsonListView
from app.risk.models import RiskModel


class RiskModelRESTView(JsonListView):
    model = RiskModel
    # response_class = JsonResponse

    # def get(self, request, *args, **kwargs):
    #
    #
    #     return JsonResponse({'status': 'success'})

    def post(self, request, *args, **kwargs):
        pass

