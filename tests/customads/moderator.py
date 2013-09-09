from geoads.contrib.moderation.moderator import AdModerator
from moderation import moderation
from .models import TestModeratedAd


moderation.register(TestModeratedAd, AdModerator)
