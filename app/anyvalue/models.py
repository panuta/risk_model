from decimal import Decimal

from dateutil.parser import parse
from django.db import models
from functools import reduce

from django.db.models import Q

from app.anyvalue.fields import AnyValueTypeField


class AnyValueFieldManager(models.Manager):
    def filter(self, *args, **kwargs):
        new_args = list(args)

        for attr in dir(self.model):
            if isinstance(getattr(self.model, attr), AnyValueTypeField):
                attr_value = kwargs.pop(attr, None)
                if attr_value:
                    q_list = []

                    # Text value
                    str_value = str(attr_value)
                    q_list.append({'value_text': str_value})

                    # Decimal value
                    try:
                        decimal_value = Decimal(attr_value)
                    except:
                        pass
                    else:
                        q_list.append({'value_number': decimal_value})

                    # Date value
                    try:
                        date_value = parse(attr_value)
                    except:
                        pass
                    else:
                        q_list.append({'value_date': date_value})

                    q = reduce(lambda x, y: x | y, [Q(**k) for k in q_list])
                    new_args.append(q)

        args = new_args
        return super().filter(*args, **kwargs)


class AnyValueEnum(models.Model):
    pass


class AnyValueEnumChoice(models.Model):
    field = models.ForeignKey(AnyValueEnum, on_delete=models.CASCADE)
    value = models.CharField(max_length=128)

    class Meta:
        unique_together = ('field', 'value')

    def __str__(self):
        return self.value
