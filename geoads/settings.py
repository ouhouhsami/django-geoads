# ads app settings file

from django.conf import settings

# used to redirect to profile when ad is deleted and other cases (see in views)
ADS_PROFILE_URL = getattr(settings, 'ADS_PROFILE_URL', '/accounts/')
ADS_PROFILE_SIGNUP = getattr(settings, 'ADS_PROFILE_SIGNUP', '/accounts/signup/')
