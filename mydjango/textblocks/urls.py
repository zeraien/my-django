#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('mydjango.textblocks.views',
	url(r'^(?P<textblock_id>\d+)/$','display',name="textblock_display"),
	url(r'^save/$','save',name="textblock_save"),
	url(r'^(?P<textblock_id>\d+)/delete/$','delete',name="textblock_delete"),
	url(r'^(?P<textblock_id>\d+)/edit/$','edit',name="textblock_edit"),
	url(r'^drop/$','drop',name="textblock_drop"),
	url(r'^reset_cache/$','reset_cache',name="textblock_reset_cache"),
)

