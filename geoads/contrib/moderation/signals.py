#-*- coding: utf-8 -*-
from django.dispatch import Signal

moderation_in_progress = Signal(providing_args=['ad'])