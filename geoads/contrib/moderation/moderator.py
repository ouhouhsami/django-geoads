#-*- coding: utf-8 -*-
from moderation.moderator import GenericModerator

from geoads.events import ad_post_save_handler

from .managers import ModeratedAdManager
from .signals import moderation_in_progress


class AdModerator(GenericModerator):
    fields_exclude = ['update_date', 'create_date', 'delete_date']
    visibility_column = 'visible'
    # Allows to have geomanager and moderationmanager simultaneously
    moderation_manager_class = ModeratedAdManager

    def inform_moderator(self,
                         content_object,
                         extra_context=None):
    	super(AdModerator,self).inform_moderator(content_object, extra_context=None)
    	moderation_in_progress.send(sender=content_object.__class__, ad=content_object)

    def inform_user(self, content_object,
                    user,
                    extra_context=None):
        """I "remove" this method, because post_moderation signal
        is the only piece I need to send email using
        mail factory (and centralize all emails sendings).
        """
        pass


def post_moderation_abstract_handler(sender, instance, status, **kwargs):
    ad_post_save_handler(sender, instance)
