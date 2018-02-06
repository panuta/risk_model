from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelBase


class ModelJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        if isinstance(obj.__class__, ModelBase):
            return obj.to_dict()

        return super().default(obj)
