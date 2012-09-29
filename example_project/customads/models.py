from django.db import models
from geoads.models import Ad


class TestAd(Ad):
    brand = models.CharField(max_length=255, null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('view', [str(self.id)])


class TestBooleanAd(Ad):
    boolean = models.BooleanField()

from geoads.receivers import *
