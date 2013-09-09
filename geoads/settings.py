# ads app settings file
from django.conf import settings

BYPASS_GEOCODE = getattr(settings, 'BYPASS_GEOCODE', False)
GEOCODE = getattr(settings, 'GEOCODE', 'nominatim')

GEOADS_ASYNC = getattr(settings, 'GEOADS_ASYNC', False)
