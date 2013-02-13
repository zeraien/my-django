import datetime
import json
import logging
from django import forms
from django.utils.translation import ugettext as _
from django.db import models
from django.core import exceptions as django_exceptions

class JSONFieldBase(models.Field):
    __metaclass__ = models.SubfieldBase
    empty_strings_allowed = False
    prefix = "$json$"
    default_error_messages = {
        'invalid': _("This value must be a valid JSON string."),
    }
    description = _("A JSON Object")

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if value is not None and value != '':
            try:
                value = JSONFieldBase.prefix+json.dumps(value)
            except (ValueError, TypeError):
                raise django_exceptions.ValidationError(self.error_messages['invalid'])

        return value

    def to_python(self, value):
        is_str = type(value) in (str, unicode)
        if is_str and value.startswith(JSONFieldBase.prefix):
            value = value[len(JSONFieldBase.prefix):]
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                # If an error was raised, just return the plain value
                logging.getLogger(__name__).warning('Error processing value [%s] (first 20 chars) of type [%s] for field [%s] (#1)' % (value[:20], type(value), self.verbose_name), exc_info=True)
                return value

        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        return super(JSONFieldBase, self).formfield(**defaults)

class BigJSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        super(BigJSONField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "mydjango.db.models.BigJSONField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

class JSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        super(JSONField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "mydjango.db.models.JSONField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

class TimeStampedModel(models.Model):
    """
    Contains `created_at` and `last_modified_at` fields.
    """
    class Meta:
        abstract = True
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True, editable=False, db_index=True)
    last_modified_at = models.DateTimeField(auto_now=True, db_index=True)
