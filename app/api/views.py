import json
from json import JSONDecodeError

from django.core.paginator import EmptyPage
from django.http import JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from app.api.json import ModelJSONEncoder
from app.api.models import SerializableMixin


class JsonResponseMixin:
    def render_to_response(self, data, **kwargs):
        if data:
            return JsonResponse(data, safe=False, encoder=ModelJSONEncoder, **kwargs)
        else:
            return HttpResponse(data, **kwargs)


# Remove CSRF definitely not best-practices but let's make it simple just for this challenge
@method_decorator(csrf_exempt, name='dispatch')
class JsonListView(JsonResponseMixin, BaseListView):
    paginate_by = 20
    paginate_url_name = None

    def render_to_response(self, data, **kwargs):
        response = super().render_to_response(data, **kwargs)
        response['Allow'] = 'GET, POST'
        return response

    @classmethod
    def _build_url_with_page(cls, request, url_name, page_number):
        return '{scheme}://{host}{url}?page={page}'.format(
            scheme=request.scheme,
            host=request.get_host(),
            url=reverse(url_name),
            page=page_number)

    def get_context_data(self, object_list=None, **kwargs):
        context = {}

        queryset = object_list if object_list is not None else self.object_list
        context['count'] = queryset.count()

        page_size = self.kwargs.get('limit') or self.request.GET.get('limit') or self.get_paginate_by(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            try:
                context['previous'] = page.previous_page_number()
            except EmptyPage:
                context['previous'] = None
            try:
                context['next'] = page.next_page_number()
            except EmptyPage:
                context['next'] = None
        else:
            context['previous'] = None
            context['next'] = None

        if self.paginate_url_name:
            if context['previous']:
                context['previous'] = JsonListView._build_url_with_page(
                    self.request, self.paginate_url_name, context['previous'])
            if context['next']:
                context['next'] = JsonListView._build_url_with_page(
                    self.request, self.paginate_url_name, context['next'])

        context['results'] = queryset

        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except JSONDecodeError as e:
            return self.render_to_response({'error': 'JSON decode error: {}'.format(str(e))}, status=500)

        validated_data, errors = self.validate_on_create(self.request, data, *args, **kwargs)
        if errors:
            return self.render_to_response(errors, status=400)

        try:
            obj = self.perform_create(request, validated_data, *args, **kwargs)
        except Exception as e:
            return self.render_to_response({'error': str(e)}, status=500)

        if obj:
            if isinstance(obj, SerializableMixin):
                return_data = obj.to_dict()
            else:
                return_data = str(obj)
        else:
            return_data = {}

        return self.render_to_response(return_data, status=201)

    def validate_on_create(self, request, data, *args, **kwargs):
        return data, {}

    def perform_create(self, request, validated_data, *args, **kwargs):
        raise NotImplementedError


@method_decorator(csrf_exempt, name='dispatch')
class JsonDetailView(JsonResponseMixin, BaseDetailView):
    pk_field = 'pk'

    def render_to_response(self, data, **kwargs):
        response = super().render_to_response(data, **kwargs)
        response['Allow'] = 'GET, PUT, DELETE'
        return response

    def get_context_data(self, **kwargs):
        context = {}

        if self.object:
            context.update(self.object.to_dict())

        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return context

    def get_object(self, queryset=None):
        queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)

        if pk is not None:
            queryset = queryset.filter(**{self.pk_field: pk})

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404('No {verbose_name} found matching the query'.format(
                verbose_name=queryset.model._meta.verbose_name))

        return obj

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
        except Http404:
            return self.render_to_response({'error': 'Object not found'}, status=404)
        except Exception as e:
            return self.render_to_response({'error': str(e)}, status=500)

        return response

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except JSONDecodeError as e:
            return self.render_to_response({'error': 'JSON decode error: {}'.format(str(e))}, status=500)

        try:
            model_object = self.get_object()
        except Http404 as e:
            return self.render_to_response({'error': str(e)}, status=404)

        validated_data, errors = self.validate_on_update(self.request, model_object, data, *args, **kwargs)
        if errors:
            return self.render_to_response(errors, status=400)

        try:
            obj = self.perform_update(request, model_object, validated_data, *args, **kwargs)
        except Exception as e:
            return self.render_to_response({'error': str(e)}, status=500)

        if obj:
            if isinstance(obj, SerializableMixin):
                return_data = obj.to_dict()
            else:
                return_data = str(obj)
        else:
            return_data = {}

        return self.render_to_response(return_data)

    def validate_on_update(self, request, model_object, data, *args, **kwargs):
        return data, {}

    def perform_update(self, request, model_object, validated_data, *args, **kwargs):
        raise NotImplementedError

    def delete(self, request, *args, **kwargs):
        try:
            model_object = self.get_object()
        except Http404 as e:
            return self.render_to_response({'error': str(e)}, status=404)

        data = None

        validated_data, errors = self.validate_on_delete(self.request, model_object, data, *args, **kwargs)
        if errors:
            return self.render_to_response(errors, status=400)

        try:
            self.perform_delete(request, model_object, validated_data, *args, **kwargs)
        except Exception as e:
            return self.render_to_response({'error': str(e)}, status=500)

        return self.render_to_response('', status=204)

    def validate_on_delete(self, request, model_object, data, *args, **kwargs):
        return data, {}

    def perform_delete(self, request, model_object, validated_data, *args, **kwargs):
        raise NotImplementedError
