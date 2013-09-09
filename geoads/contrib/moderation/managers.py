#-*- coding: utf-8 -*-
from moderation.managers import ModerationObjectsManager
from django.contrib.gis.db.models import GeoManager


class ModeratedAdManager(ModerationObjectsManager, GeoManager):
    """
    Manager for Ad with moderation feature and geo enabled
    """
    pass
