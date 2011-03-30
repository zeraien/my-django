from django.contrib import admin
from django.utils.translation import ugettext as _
from mydjango.textblocks.models import *

class InlineURLInstance(admin.TabularInline):
    model = URLItem
    verbose_name = "More URL"
    verbose_name_plural = "More URLs"
# class InlineModelInstance(admin.TabularInline):
#     model = ModelItem
class InlineContent(admin.StackedInline):
    model = Content
    
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'min_width', 'max_width')
    search_fields = ('name','title')
    prepopulated_fields = {'name':('title',)}
    list_filter = ('min_width', 'max_width',)
admin.site.register(TextBlockTemplate, TemplateAdmin)

def _localizations(instance):
	_list = []
	for c in instance.localized_content.all():
		_list.append(c.language_code)
	return _list and ', '.join(_list) or _("<----")
_localizations.short_description = _("localizations")

class TextBlockAdmin(admin.ModelAdmin):
    list_display = ('url', 'position', 'language', _localizations,'sort_order', 'note', 'updated', 'content')
    list_filter = ('position', 'localized_content__language_code', 'language',)
    save_on_top = True
    list_select_related = True
    ordering = ['-updated', 'sort_order', 'url']
    list_display_links = ("url", "position")
    search_fields = ('url','^position','note','content')
    inlines = [InlineContent, InlineURLInstance]#, InlineModelInstance]

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

