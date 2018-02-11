from django.urls import path

from . import views

app_name = 'risk.api'
urlpatterns = [
    path('models/', views.RiskModelListView.as_view(), name='model-list'),
    path('models/<str:model_uuid>/', views.RiskModelDetailView.as_view(), name='model-detail'),

    path('models/<str:model_uuid>/objects/', views.RiskModelObjectListView.as_view(), name='object-list'),
    path('models/objects/<str:object_uuid>/', views.RiskModelObjectDetailView.as_view(), name='object-detail'),
]
