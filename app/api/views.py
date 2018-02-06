import json

from django.core.paginator import EmptyPage
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from app.api.json import ModelJSONEncoder
from app.api.models import SerializableMixin


class JsonResponseMixin:
    def render_to_response(self, data, **kwargs):
        return JsonResponse(data, safe=False, encoder=ModelJSONEncoder, **kwargs)


class JsonListView(JsonResponseMixin, BaseListView):
    paginate_by = 20
    paginate_url_name = None

    @classmethod
    def _build_url_with_page(cls, request, url_name, page_number):
        return '{scheme}://{host}{url}?page={page}'.format(
            scheme=request.scheme,
            host=request.get_host(),
            url=reverse(url_name),
            page=page_number)

    def get_context_data(self, object_list=None, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        queryset = object_list if object_list is not None else self.object_list
        kwargs['count'] = queryset.count()

        page_size = self.get_paginate_by(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            try:
                kwargs['previous'] = page.previous_page_number()
            except EmptyPage:
                kwargs['previous'] = None
            try:
                kwargs['next'] = page.next_page_number()
            except EmptyPage:
                kwargs['next'] = None
        else:
            kwargs['previous'] = None
            kwargs['next'] = None

        if self.paginate_url_name:
            if kwargs['previous']:
                kwargs['previous'] = JsonListView._build_url_with_page(
                    self.request, self.paginate_url_name, kwargs['previous'])
            if kwargs['next']:
                kwargs['next'] = JsonListView._build_url_with_page(
                    self.request, self.paginate_url_name, kwargs['next'])

        kwargs['results'] = queryset
        return kwargs

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # TODO : Validate data
        validated_data = data

        obj = self.perform_create(request, validated_data, *args, **kwargs)

        if obj:
            if isinstance(obj, SerializableMixin):
                return_data = obj.to_dict()
            else:
                return_data = str(obj)
        else:
            return_data = {}

        return self.render_to_response(return_data, status=201)

    def perform_create(self, request, data, *args, **kwargs):
        raise NotImplementedError


class JsonDetailView(JsonResponseMixin, BaseDetailView):
    pass
