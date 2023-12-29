from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

class LogEntry(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now)
    level = models.CharField(max_length=20,db_index=True)
    ip_address = models.GenericIPAddressField(null=True,blank=True)
    message = models.TextField()
        
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')

