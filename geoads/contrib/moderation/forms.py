#-*- coding: utf-8 -*-
from geoads.forms import BaseAdForm
from moderation.forms import BaseModeratedObjectForm


class BaseModeratedAdForm(BaseModeratedObjectForm, BaseAdForm):
    """
    Base Moderated Ad Form
    """
    pass
