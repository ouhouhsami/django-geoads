# coding=utf-8
""" Ads app admin module """

from django.contrib import admin
from ads.models import AdSearch, AdContact, AdPicture


admin.site.register(AdSearch)
admin.site.register(AdContact)
admin.site.register(AdPicture)
