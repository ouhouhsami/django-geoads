# coding=utf-8
""" Ads specific filters for search"""

from django.contrib.gis.geos import fromstr
from django_filters.filters import Filter

import floppyforms


class LocationFilter(Filter):
    """Location filter
    Used for geo filtering inside shape
    """
    field_class = floppyforms.gis.PolygonField

    def filter(self, qs, value):
        lookup = 'within'
        if not value:
            return qs
        else:
            value = fromstr(value)
            return qs.filter(**{'%s__%s' % (self.name, lookup): value})


class BooleanForNumberFilter(Filter):
    """Boolean for number filter
    Used to filter if a number field is set or not (null or not)
    """
    def filter(self, qs, value):
        if value is None:
            return qs
        else:
            return qs.filter(**{'%s__isnull' % (self.name): not(value)})
