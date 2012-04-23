from moderation import moderation
from moderation.moderator import GenericModerator
from customads.models import TestAd

class TestAdModerator(GenericModerator):
    fields_exclude = ['update_date', 'create_date', 'delete_date']
    notify_moderator = True
    notify_user = True
    visibility_column = 'visible'


moderation.register(TestAd, TestAdModerator)