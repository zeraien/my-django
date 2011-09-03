#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils import html

from django import template
register = template.Library()

from mydjango.logging import log
from mydjango.textblocks.models import TextBlock, TextBlockTemplate

@register.simple_tag
def parse_as_template(textblock, context):
    from django.template import Context, loader
    try:
        template_ = loader.get_template_from_string(textblock.html)
        return template_.render(Context(context))
    except:
        log.exception_warn("Failed to render text block template.")
    return ''

def _process_url(url):
    if url is None: url = '*'
    url = url.strip()
    if url == '': url = '/'
    elif url[0:4] == "url:":
        parts = url.split('/',1)
        url_part = parts[0].split(':')[1]
        if len(parts) > 1:
            after_part = parts[1]
        url = u"%s/%s" % (reverse(url_part).rstrip('/'), after_part)
    return url

def _get_textblock(context, url, position, raw = False, exclude_url_parts = 0, host = None):
    if host is None:
        host = context['request'].get_host()
       
    url = _process_url(url) 
    
    position = slugify(position)
    
    new_sort_order = 0;
    _cache_str = 'textblock_%s_%s_%s' % (url, position, host)
    cached_textblocks = cache.get(_cache_str, None)
    if cached_textblocks is None or context['request'].GET.get('reset_textblock_cache') is not None:
        # Grab all textblocks for this URL, cache them and return the ones for the requested position.
        # This is useful since caching is only done rarely 
        qs = TextBlock.objects.get_all_for_url(url,position=position).order_by('url_items__sort_order', 'sort_order')
        blocks = {position:[]}
        for tb in qs:
            blocks[position].append(tb)
            if tb.sort_order > new_sort_order:
                new_sort_order = tb.sort_order
        for pos_, tblocks in blocks.items():
            _tmp_cache_str = 'textblock_%s_%s_%s' % (url, pos_, host)
            cache.set(_tmp_cache_str, list(tblocks), 3600)
        qs = blocks.get(position, [])
        count = len(qs)
    else:
        qs = cached_textblocks
        count = len(qs)
        
    user = context['request'].user
    new_context = {
        'context': context,
        'textblock_count': count,
        'textblocks': qs,
        'can_edit': user.has_perm("textblocks.change_textblock"),
        'can_add': user.has_perm("textblocks.add_textblock"),
        'can_delete': user.has_perm("textblocks.delete_textblock"),
        'view_options': context.get('view_options',None),
        'templates': TextBlockTemplate.objects.all(),
        'position': position
    }

    if exclude_url_parts > 0:
        parts = url.strip('/').split('/')
        if exclude_url_parts < len(parts):
            url = '/'+'/'.join(parts[:(exclude_url_parts*-1)])+'/'
        else:
            url = '/'
    new_context['new_textblock'] = TextBlock(url=url,sort_order=new_sort_order+1, position=position)
    new_context['named_textblocks'] = TextBlock.objects.exclude(note__isnull=True).exclude(note='').order_by('note')
    return new_context

@register.inclusion_tag('_textblock_toggle_buttons.html',takes_context=True)
def textblock_edit_mode_button(context):
    return context

@register.simple_tag
def textstring(name):
    try:
        cache_id = "textstring_%s" % name
        content = cache.get(cache_id)
        if content is None:
            content = TextBlock.objects.filter(url=name).only('content').latest().content
            cache.set(cache_id, content, 3600)
        return content
    except ObjectDoesNotExist, e:
        pass

@register.inclusion_tag('_textblock.html',takes_context=True)
def named_textblock(context, name, position = None):
    """A text block that is not bound to a URL, but a name and position. Position is optional."""
    return _get_textblock(context=context, url=name, position=position)

@register.inclusion_tag('_textblock.html',takes_context=True)
def textblock(context, position, exclude_url_parts = 0):
    """Display a text block for the current URL and position. Some URL's contain wild cards."""
    return _get_textblock(context=context, url=context['request'].path, position=position, exclude_url_parts=exclude_url_parts)

@register.inclusion_tag('_textblock.html', takes_context=True)
def textblock_creator(context):
    """Display a text block creation form. The newly created text block can be drag and dropped on to any text block position on the site."""
    return _get_textblock(context=context, url=context['request'].path, position='new')
    
@register.inclusion_tag('_textblock_scripts.html',takes_context=True)
def load_textblock_support(context):
    """Prints out CSS and HTML code needed for text block administration to work"""
    return context
