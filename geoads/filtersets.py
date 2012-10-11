# coding=utf-8
from django.db import models
from django.contrib.gis.db import models

import django_filters
from django_filters.filterset import FilterSetMetaclass, FilterSetOptions

from geoads.models import Ad
from geoads.filters import LocationFilter


class GeoAdsFilterSetMetaclass(FilterSetMetaclass):
    """
    This class add a filterset attribute on the model,
    so that the model is 'aware' of it filterclass
    """
    def __new__(cls, name, bases, attrs):
        new_class = super(GeoAdsFilterSetMetaclass, cls).__new__(cls, name,
            bases, attrs)
        opts = new_class._meta = FilterSetOptions(getattr(new_class, 'Meta',
            None))
        opts.model.filterset = new_class
        return new_class


class AdFilterSet(django_filters.FilterSet):
    """
    Ad FilterSet specific class
    """
    __metaclass__ = GeoAdsFilterSetMetaclass

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
