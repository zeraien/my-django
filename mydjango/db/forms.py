from django.core import validators
import json
from django import forms
from django.core import exceptions as django_exceptions
from django.utils.translation import ugettext as _

class JSONFormField(forms.CharField):
    default_error_messages = {
        'invalid': _("This value must be a valid JSON string."),
    }
    description = _("A JSON Object")

    def clean(self, value):
        return super(JSONFormField, self).clean(value)

    def bound_data(self, data, initial):
        if data in validators.EMPTY_VALUES:
            return None
        try:
            data = json.loads(data)
        except (ValueError, TypeError):
            pass

        return data

    def prepare_value(self, value):
        if value in validators.EMPTY_VALUES:
            return u''
        try:
            value = json.dumps(value)
        except (ValueError, TypeError):
            pass
        return value

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            raise django_exceptions.ValidationError(self.error_messages['invalid'])
        return value
