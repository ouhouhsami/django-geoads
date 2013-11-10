from geoads.contrib.moderation.moderator import AdModerator
from moderation import moderation
from customads.models import TestModeratedAd


moderation.register(TestModeratedAd, AdModerator)
