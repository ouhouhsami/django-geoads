# coding=utf-8
"""
Ads app filtersets module

This module provides default filterset 'AdFilterSet' to work with Ad models.
"""
#from django.db import models
from django.contrib.gis.db import models

import django_filters

from geoads.models import Ad
from geoads.filters import LocationFilter


class AdFilterSet(django_filters.FilterSet):
    """
    Ad FilterSet specific class
    """
    # this set use of LocationFilter for PointField
    filter_overrides = {
        models.PointField: {
            'filter_class': LocationFilter
        }
    }

    def __len__(self):
        return len(self.qs)

    def __getitem__(self, key):
        return self.qs[key]

    class Meta:
        model = Ad  # this must be set by the children class
