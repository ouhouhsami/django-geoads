#-*- coding: utf-8 -*-
"""
Ads specific filters for search
"""
from django.contrib.gis.geos import fromstr
#from django.contrib.gis.db.models.fields import PolygonField
from django_filters.filters import Filter

from django import forms


class LocationFilter(Filter):
    """
    Location filter
    Used for geo filtering inside shape
    """
    # TODO: below, ugly hack for the moment, should be field_class = PolygonField with django 1.6
    field_class = forms.Field

    def filter(self, qs, value):
        lookup = 'within'
        if not value:
            return qs
        value = fromstr(value)
        return qs.filter(**{'%s__%s' % (self.name, lookup): value})


class BooleanForNumberFilter(Filter):
    """
    Boolean for number filter
    Used to filter if a number field is set or not (null or not)
    """
    def filter(self, qs, value):
        if value is None:
            return qs
        return qs.filter(**{'%s__isnull' % (self.name): not(value)})
