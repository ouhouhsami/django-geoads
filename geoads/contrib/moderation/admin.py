#-*- coding: utf-8 -*-
from django.contrib import admin
from moderation.admin import ModerationAdmin
from geoads.contrib.moderation.models import ModeratedAd


def get_subclasses(classes, level=0):
    """
    Return the list of all subclasses given class (or list of classes) has.
    Inspired by this question:
    http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
    """
    # for convenience, only one class can can be accepted as argument
    # converting to list if this is the case
    if not isinstance(classes, list):
        classes = [classes]

    if level < len(classes):
        classes += classes[level].__subclasses__()
        return get_subclasses(classes, level + 1)
    else:
        return classes


for mod in get_subclasses(ModeratedAd):
    if mod != ModeratedAd:
        admin.site.register(mod, ModerationAdmin)
