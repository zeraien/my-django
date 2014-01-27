from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.cache import cache

from django.conf import settings

# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes import generic

import re

class TextBlockManager(models.Manager):
    def get_all_for_url(self, url, **kwargs):
        q = Q(url='*')
        if url == '/':
            q |= Q(url='/')
        else:
            url_parts = url.strip('/').split('/')
            query_url = '/'
            final = len(url_parts)
            i = 0
            for part in url_parts:
                i += 1
                query_url += '%s' % part
                q |= Q(url='%s/*' % query_url)
                if i == final:
                    q |= Q(url='%s/' % query_url)
                q |= Q(url='%s*' % query_url)
                query_url += '/'
        
        base_qs = self.select_related(depth=1).filter(is_hidden=False).distinct()

        hidden_tbs = URLItem.objects.filter(is_hidden=True).filter(q).filter(**kwargs).distinct()

        base_qs_filtered = base_qs.filter(q).filter(**kwargs).exclude(url_items__in=hidden_tbs)

        visible_tbs = base_qs.filter(url_items__in=URLItem.objects.filter(is_hidden=False).filter(q).filter(**kwargs).distinct())|base_qs_filtered
        if visible_tbs.count() > 0:
            return visible_tbs.exclude(url_items__in=hidden_tbs).order_by('url_items__sort_order', 'sort_order')
        else:
            return base_qs_filtered.order_by('sort_order')
        
class TextBlock(models.Model):
    objects = TextBlockManager()
    url = models.CharField(_('URL'),max_length=255,help_text=_("This is a URL to the page(s) where this text block will appear. Specify the full URL of the page, or to display on all pages beneath a certain path, add an asterisk (*) at the end of the URL. Best way to create or edit a text block, is to go to the page in question and click the edit link next to the text block you wish to edit or create."),db_column="slug", db_index=True)
    position = models.SlugField(_("position"),max_length=50, help_text=_("Where on the page will this text block appear."),unique=False,db_index=True)
    note = models.CharField(_('note'),max_length=255,help_text=_("This should contain some information about what page this text block applies to."), blank=True, null=True)
    content = models.TextField(_('content'), help_text=_("Use the markup language that you have selected below."), blank=True, null=True)
    html = models.TextField(editable=False, blank=True)
    language = models.CharField(max_length=5, verbose_name=_('language code'), default=settings.LANGUAGE_CODE, blank=True, null=True)
    markup_language = models.CharField(_("markup language"),max_length=10,default="markdown",choices=(('textile',_("Textile")), ("markdown",_("Markdown")), (None,_("HTML only"))),blank=True,null=True)

    sort_order = models.SmallIntegerField(_("sort order"), default=0)

    is_hidden = models.BooleanField(_("hidden"), default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_name(self):
        return u"%s @ %s" % (self.position, self.url)
        
    def get_edit_url(self):
        if self.pk:
            return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.module_name), args=(self.pk,))
        else:
            import urllib
            qs = urllib.urlencode({'position':self.position, 'url': self.url, 'sort_order': self.sort_order})
            return reverse('admin:%s_%s_add' % (self._meta.app_label, self._meta.module_name))+"?"+qs
    
    def get_absolute_url(self):
        url = "/"
        if self.url == "":
            url = "/"
        elif "*" in self.url:
            url = self.url.split("*",1)[0]
        else:
            url = self.url
        
        return u"%s?reset_textblock_cache=1#textblock_%s" % (url, self.position)
        
    def __unicode__(self):
        return self.get_name()
    
    class Meta:
        verbose_name = _('text block')
        verbose_name_plural = _('text blocks')
        ordering = ['sort_order', '-updated', 'url']
        get_latest_by = 'updated'
        #unique_together = ('url','position')

def textblock_pre_save(sender, instance, **kwargs):
    cache.clear()

    if instance.markup_language == "markdown":
        import markdown
        instance.html = markdown.markdown(instance.content)
    elif instance.markup_language == 'textile':
        import textile
        instance.html = textile.textile(instance.content)
    else:
        instance.html = instance.content
pre_save.connect(textblock_pre_save, sender=TextBlock)

# class ModelItem(models.Model):
#     content_type = models.ForeignKey(ContentType, null=True, blank=True)
#     object_id = models.PositiveIntegerField(null=True, blank=True)
#     content_object = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
#     
#     textblock = models.ForeignKey(TextBlock)
#     sort_order = models.SmallIntegerField(_("sort order"))
#     placeholder = models.SlugField(_("placeholder"),unique=False, db_index=True)
#     is_hidden = models.BooleanField(_("hidden"), default=False)
#

class Content(models.Model):
    class Meta:
        verbose_name = _("Content")
        verbose_name_plural = _("Content entries")
    textblock = models.ForeignKey(TextBlock, related_name="localized_content")
    content = models.TextField(_('content'), help_text=_("Use the markup language that you have selected below."), blank=True, null=True)
    html = models.TextField(editable=False, blank=True)
    language_code = models.CharField(max_length=5, verbose_name=_('language code'), default=settings.LANGUAGE_CODE, blank=True, null=True)
    markup_language = models.CharField(_("markup language"),max_length=10,default="markdown",choices=(('textile',_("Textile")), ("markdown",_("Markdown")), (None,_("HTML only"))),blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "content for %s" % self.textblock


class URLItem(models.Model):
    url = models.CharField(_('URL'),max_length=255)
    sort_order = models.SmallIntegerField(_("sort order"), default=0)
    position = models.SlugField(_("position"), unique=False, db_index=True)
    is_hidden = models.BooleanField(_("hidden"), default=True)
    textblock = models.ForeignKey(TextBlock, related_name="url_items")
    def __unicode__(self):
        return u"%s @ %s%s" % (self.position, self.url, (self.is_hidden and u' [%s]'%_("hidden") or ""))

class TextBlockTemplate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(_('title'),max_length=255,help_text=_("This should contain some basic information about what page this template does."))
    name = models.SlugField(_("unique name"),max_length=50, help_text=_("This will in the future be used for linking templates to text blocks."),unique=True,db_index=True)
    content = models.TextField(_('content'), help_text=_("Use any markup language that you can select below."), blank=True, null=True)
    min_width = models.IntegerField(_("min width"), blank=True, default=0, help_text=_("minimum width recommended for this template"))
    max_width = models.IntegerField(_("max width"), blank=True, default=0, help_text=_("maximum width recommended for this template"))
    is_disabled = models.BooleanField(_("disabled"), default=False, help_text=_("Template will not be displayed in textblock lists"))
    
    def get_available_fields(self):
        prog = re.compile("(\[\[[\w_-]+\]\])")
        results = re.findall(prog, self.content)

        field_names = []
        for item in results:
            field_names.append(item.strip('[]\s\t'))
        return field_names
    
    def __unicode__(self):
        return self.title

    class Meta:
        db_table = "textblocks_template"
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ['name']
        get_latest_by = 'updated'
