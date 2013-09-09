#-*- coding: utf-8 -*-
from moderation.signals import post_moderation

from .moderator import post_moderation_abstract_handler


def moderated_geoads_register(model_class):
    post_moderation.connect(post_moderation_abstract_handler, dispatch_uid="post_moderation_abstract_handler")
