# ads app settings file
from django.conf import settings

GEOCODE = getattr(settings, 'GEOCODE', 'nominatim')

GEOADS_ASYNC = getattr(settings, 'GEOADS_ASYNC', False)
