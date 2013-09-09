from django.db import models

from geoads.models import Ad
from geoads.register import geoads_register

from geoads.contrib.moderation.models import ModeratedAd
from geoads.contrib.moderation.register import moderated_geoads_register


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


class TestModeratedAd(ModeratedAd):
    brand = models.CharField(max_length=255, null=True, blank=True)

    default_filterset = 'tests.customads.filtersets.TestAdFilterSet'

    def get_full_description(self, instance=None):
        return self.brand


geoads_register(TestAd)
geoads_register(TestNumberAd)
moderated_geoads_register(TestModeratedAd)