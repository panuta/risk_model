from django.contrib import admin

from .models import RiskModel, RiskModelField, RiskModelObject, RiskModelObjectValue

admin.site.register(RiskModel)
admin.site.register(RiskModelField)
admin.site.register(RiskModelObject)
admin.site.register(RiskModelObjectValue)
