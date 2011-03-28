from django.contrib import admin
from mydjango.logging.models import *

def log_message(instance):
    return instance.message
# log_message.short_description = _('message')
log_message.allow_tags = True

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('level','ip_address','created_at', log_message)
    list_filter = ('level',)
    list_display_links = ('level','ip_address','created_at')
    search_fields = ('=ip_address','message')
    
admin.site.register(LogEntry, LogEntryAdmin)
