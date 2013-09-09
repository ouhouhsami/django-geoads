#-*- coding: utf-8 -*-
from django.http import Http404

from geoads.views import AdUpdateView

from .forms import BaseModeratedAdForm


class ModeratedAdUpdateView(AdUpdateView):
    """
    Class base update moderated ad
    """
    form_class = BaseModeratedAdForm

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        # We shoud inherit from method get_object of parent class ...
        obj = self.model.unmoderated_objects.get(id=self.kwargs['pk'])

        if not obj.user == self.request.user:
            raise Http404

        return obj
