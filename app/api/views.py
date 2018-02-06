from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from app.api.json import ModelJSONEncoder


class JsonResponseMixin:
    def render_to_response(self, data):
        return JsonResponse(data, safe=False, encoder=ModelJSONEncoder)


class JsonListView(JsonResponseMixin, BaseListView):
    def get_context_data(self, object_list=None, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        queryset = object_list if object_list is not None else self.object_list

        kwargs['count'] = queryset.count()
        kwargs['results'] = queryset

        # TODO : is_paginated, next, previous
        return kwargs


class JsonDetailView(JsonResponseMixin, BaseDetailView):
    pass
