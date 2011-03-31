import os.path
import json as simplejson

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponsePermanentRedirect
from django.core.xheaders import populate_xheaders

from functools import wraps


def render(request, template, context = {}, ignore_ajax = False, obj=None, **render_kwargs):
    if request.is_ajax() and not ignore_ajax:
        basename = os.path.basename(template)
        dirname = os.path.dirname(template)
        template = "%s/_%s"%(dirname,basename)
        response = render_to_response(template, context)
    else:
        response = render_to_response(template, context, context_instance=RequestContext(request), **render_kwargs)
    if obj is not None:
        populate_xheaders(request, response, obj.__class__, obj.pk)
    return response
    
def permanent_redirect(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if type(to) in (str, unicode):
            return HttpResponsePermanentRedirect(to)
        else:
            return to
    return wrapper
    
def redirect(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if type(to) in (str, unicode):
            return HttpResponseRedirect(to)
        else:
            return to
    return wrapper

def render_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kw):
        _json = view_func(request, *args, **kw)
        if not isinstance(_json, str) and not isinstance(_json, dict) and not isinstance(_json, list) and not isinstance(_json, tuple):
            return _json
        mimetype = request.is_ajax() and "application/json" or "text/plain"
        return HttpResponse(simplejson.dumps(_json), mimetype=mimetype)
    return wrapper

def render_to(template_name):
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            output['request'] = request
            return render(request, template=template_name, context=output)
        return wrapper
    return renderer
