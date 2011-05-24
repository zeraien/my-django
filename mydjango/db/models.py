import datetime
import json
from django.utils.translation import ugettext as _
from django.db import models

class JSONFieldBase(models.Field):
    __metaclass__ = models.SubfieldBase
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _("This value must be a valid JSON string."),
    }
    description = _("A JSON Object")
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value)
        
    def to_python(self, value):
        if value is None or type(value) in (list, dict, tuple):
            return value
        return json.loads(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        return super(JSONFieldBase, self).formfield(**defaults)

class BigJSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        super(BigJSONField, self).__init__(*args, **kwargs)
        
    def get_internal_type(self):
        return 'TextField'

class JSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        super(JSONField, self).__init__(*args, **kwargs)
        
    def get_internal_type(self):
        return 'CharField'

class TimeStampedModel(models.Model):
    """
    Contains `created_at` and `last_modified_at` fields.
    """
    class Meta:
        abstract = True
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True)
