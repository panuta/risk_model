from django.urls import path

from . import views

app_name = 'risk'
urlpatterns = [
    path('', view=views.home, name='home'),

]
