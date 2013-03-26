from django.db import models
from geoads.models import Ad


class TestAd(Ad):
    brand = models.CharField(max_length=255, null=True, blank=True)

    default_filterset = 'tests.customads.filtersets.TestAdFilterSet'

    @models.permalink
    def get_absolute_url(self):
        return ('view', [str(self.id)])

    def get_full_description(self, instance=None):
        return self.brand


class TestNumberAd(Ad):
    number = models.IntegerField(null=True, blank=True)

    def get_full_description(self, instance=None):
        return 'number'

# VERY IMPORTANT TO PLACE THIS IMPORT AT THE BOTTOM
# so that abstract class and subclass signal dispatcher
# is available for this model
from geoads.receivers import *
