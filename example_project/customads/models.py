from django.db import models
from geoads.models import Ad


class TestAd(Ad):
    brand = models.CharField(max_length=255, null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('view', [str(self.id)])


class TestBooleanAd(Ad):
    boolean = models.BooleanField()

# VERY IMPORTANT TO PLACE THIS IMPORT AT THE BOTTOM
# so that abstract class and subclass signal dispatcher
# is available for this model
from geoads.receivers import *
