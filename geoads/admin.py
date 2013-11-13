#-*- coding: utf-8 -*-
"""
Ads app admin module
"""
from django.contrib import admin
from geoads.models import AdSearch, AdPicture, AdSearchResult


admin.site.register(AdSearch)
admin.site.register(AdPicture)
admin.site.register(AdSearchResult)
