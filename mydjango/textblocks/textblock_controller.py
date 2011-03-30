from django_url_framework import ActionController
from django.shortcuts import get_object_or_404
from mydjango.textblocks.models import TextBlock, TextBlockTemplate
from mydjango.logging import log
from django.template import Context, loader
from django.core.cache import cache

class TextblockController(ActionController):
	controller_prefix = "_"

	def _before_filter(self):
		if not self._request.user.has_perm('textblocks.change_textblock'):
			return 'Not logged in'
		return None
	
	def reset_cache(self,request):
		if hasattr(cache._cache, 'flush_all'):
			cache._cache.flush_all()
			return "OK!"
		return "Not flushable cache... Just wait, or restart the server?"
	
	def display(self, request, id):
		textblock = get_object_or_404(TextBlock.objects,id=id)
		self._object = textblock
		
		position = "foo"
		new_context = {
		'context': {'request':request, 'user':request.user},
		'textblock_count': 1,
		'textblocks':[textblock],
		#'perms': self._template_context.get('perms', None),
		#'view_options': self._template_context.get('view_options',None),
		'templates': TextBlockTemplate.objects.all(),
		'position': position
		}
		
		return new_context
		# try:
		# 	template_ = loader.get_template_from_string(textblock.html)
		# 	return template_.render(Context(context))
		# except:
		# 	log.exception_warn("Failed to render text block template.")
		# 	return 'Failed to render text block'
	display.template_name = "_textblock.html"
	display.ignore_ajax = True
	display.mimetype = 'text/html'
	
	def edit(self, request, id):
		textblock = get_object_or_404(TextBlock.objects,id=id)
		self._object = textblock
		return {'textblock':textblock}
	#category.urlconf = [r'category/(?P<slug>[-\w]+)/$']
	#category.erase_urlconfs = True
	edit.template_name = "textblock_inline_edit.html"
	edit.ignore_ajax = True

	def save(self, request):
		textblock_id = request.POST.get('id')
		textblock = get_object_or_404(TextBlock.objects,id=textblock_id)
		textblock.content = request.POST.get('content')
		textblock.language = request.POST.get('language', textblock.language)
		textblock.save()
		self._object = textblock
		return self._redirect(action='display',id=textblock.pk)
	save.allowed_methods = ["POST"]
	save.ignore_ajax = True
