from django.urls import path

from . import views

app_name = 'risk.api'
urlpatterns = [
    path('models/', views.RiskModelListView.as_view(), name='model-list'),
    path('models/<str:model_uuid>/', views.RiskModelDetailView.as_view(), name='model-detail'),

]
