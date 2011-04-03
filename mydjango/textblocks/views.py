#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST, require_GET
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.core.cache import cache
from django.http import HttpResponseBadRequest, HttpResponse
from mydjango.http.rendering import render_to, render_json, redirect

from mydjango.textblocks.models import TextBlock, TextBlockTemplate

@permission_required('textblocks.change_textblock')
@render_json
def reset_cache(request):
    cache.clear()
    return "OK!"

@permission_required('textblocks.change_textblock')
@render_to("_textblock.html")
def display(request, textblock_id):
    textblock = get_object_or_404(TextBlock.objects,id=textblock_id)

    new_context = {
        'context': {'request':request, 'user':request.user},
        'textblock_count': 1,
        'textblocks':[textblock],
        'can_edit': request.user.has_perm("textblocks.change_textblock"),
        'can_add': request.user.has_perm("textblocks.add_textblock"),
        'can_delete': request.user.has_perm("textblocks.delete_textblock"),
        'templates': TextBlockTemplate.objects.all(),
        'position': textblock.position
    }

    return new_context

@csrf_exempt
@require_POST
@permission_required('textblocks.change_textblock')
def drop(request):
    textblock_id = request.POST.get('id', None)
    drop_position = request.POST.get('drop_position', None)
    drop_sort_order = int(request.POST.get('drop_sort_order', 0))
    if textblock_id is None or drop_position is None:
        return HttpResponseBadRequest()
    textblock = get_object_or_404(TextBlock.objects,id=textblock_id)
    textblock.position = drop_position
    textblock.sort_order = drop_sort_order-1
    textblock.save()
    return HttpResponse()

@permission_required('textblocks.change_textblock')
@render_to("_textblock_inline_edit.html")
def edit(request, textblock_id):
    textblock = get_object_or_404(TextBlock.objects,id=textblock_id)
    return {
        'can_edit': request.user.has_perm("textblocks.change_textblock"),
        'can_add': request.user.has_perm("textblocks.add_textblock"),
        'can_delete': request.user.has_perm("textblocks.delete_textblock"),
        'textblock':textblock
    }

@csrf_exempt
@require_POST
@permission_required('textblocks.change_textblock')
@redirect
def save(request):
    textblock_id = request.POST.get('id')
    textblock = get_object_or_404(TextBlock.objects,id=textblock_id)
    textblock.content = request.POST.get('content')
    textblock.language = request.POST.get('language', textblock.language)
    textblock.save()
    return reverse(display, kwargs={'textblock_id':textblock.pk})

@csrf_exempt
@require_POST
@permission_required('textblocks.delete_textblock')
def delete(request, textblock_id):
    get_object_or_404(TextBlock.objects,id=textblock_id).delete()
    return HttpResponse()