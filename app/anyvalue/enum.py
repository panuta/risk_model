from enum import Enum

from dateutil.parser import parse


class ValueType(Enum):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    ENUM = 'enum'

    @classmethod
    def to_choices(cls):
        return ((str(value), name) for name, value in ValueType.__members__.items())

    @classmethod
    def to_value(cls, field_type, naive_value):
        if field_type == 'text':
            return str(naive_value)
        elif field_type == 'number':
            return int(naive_value)
        elif field_type == 'date':
            return parse(naive_value)
        elif field_type == 'enum':
            return int(naive_value)
        return None
