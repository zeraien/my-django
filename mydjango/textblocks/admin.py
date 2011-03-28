from django.contrib import admin
from django.utils.translation import ugettext as _
from mydjango.textblocks.models import *

class InlineURLInstance(admin.TabularInline):
    model = URLItem
    verbose_name = "More URL"
    verbose_name_plural = "More URLs"
# class InlineModelInstance(admin.TabularInline):
#     model = ModelItem

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'min_width', 'max_width')
    search_fields = ('name','title')
    prepopulated_fields = {'name':('title',)}
    list_filter = ('min_width', 'max_width',)
admin.site.register(TextBlockTemplate, TemplateAdmin)

class TextBlockAdmin(admin.ModelAdmin):
    list_display = ('url', 'position', 'sort_order', 'note', 'updated', 'content')
    list_filter = ('position', 'language',)
    save_on_top = True
    ordering = ['-updated', 'sort_order', 'url']
    list_display_links = ("url", "position")
    search_fields = ('url','^position','note','content')
    inlines = [InlineURLInstance]#, InlineModelInstance]

    fieldsets = (
        (_("position").title(), {
            'fields': ('url',('position','sort_order'),'note'),
        }),
        (_("content").title(), {
            'fields': ('content',)
        }),
        (_("metadata").title(), {
            'fields': ('language','markup_language'),
            'classes': ('collapse',)
        }),
        
    )

admin.site.register(TextBlock, TextBlockAdmin)

