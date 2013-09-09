#-*- coding: utf-8 -*-
from django.db import models

from geoads.models import Ad


class ModeratedAd(Ad):
    visible = models.BooleanField()

    class Meta:
        abstract = True
