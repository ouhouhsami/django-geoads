#-*- coding: utf-8 -*-
"""
Ads app admin module
"""
from django.contrib import admin
from geoads.models import AdSearch, AdContact, AdPicture, AdSearchResult


admin.site.register(AdSearch)
admin.site.register(AdContact)
admin.site.register(AdPicture)
admin.site.register(AdSearchResult)
