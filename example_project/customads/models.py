from django.db import models
from geoads.models import Ad


class TestAd(Ad):
    brand = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'ads'
