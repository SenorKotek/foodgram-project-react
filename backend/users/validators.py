import re
from django.core.exceptions import ValidationError


def validate_username(value):
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError(
            'Некорректные символы в username!'
        )
    if len(value) <= 2:
        raise ValidationError(
            'Имя пользователя не может быть короче трех символов'
        )
    if value == 'admin':
        raise ValidationError(
            'Имя пользователя не может быть admin.'
        )
    if value == 'foodgram':
        raise ValidationError(
            'Имя пользователя не может быть foodgram.'
        )
    return value
