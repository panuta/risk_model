from django.urls import path

from . import views

app_name = 'risk.api'
urlpatterns = [
    path('models/', views.RiskModelRESTView.as_view(), name='model-list'),

]
