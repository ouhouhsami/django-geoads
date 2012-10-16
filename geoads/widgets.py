#-*- coding: utf-8 -*-
"""
Ads widgets

"""
from django import forms
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext
from django.utils.safestring import mark_safe

from floppyforms.widgets import Input, NumberInput, NullBooleanSelect, Select
import floppyforms

from geoads.templatetags.ads_tag import create_thumbnail_image_file


class ImageWidget(forms.FileInput):
    """
    Image widget
    Used for rendering ImageField in Ad form

    """
    template = u'%(input)s<div class="thumbnail" style="float:right;"><a  href="%(image)s" target="_blank"><img class="img-polaroid" src="%(image_thumbnail)s" /></a><p>Aperçu</p></div>'

    def __init__(self, attrs=None, template=None, width=200, height=200):
        if template is not None:
            self.template = template
        self.width = width
        self.height = height
        super(ImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        input_html = super(forms.FileInput, self).render(name, value, attrs)
        if hasattr(value, 'width') and hasattr(value, 'height'):
            output = self.template % {'input': input_html, 'image': value.url,
                                      'image_thumbnail': create_thumbnail_image_file(value, 250, 150)}
        else:
            output = input_html
        return mark_safe(output)


class IndifferentNullBooleanSelect(NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', ugettext(u'Indifférent')),
                   (u'2', ugettext(u'Oui')),
                   (u'3', ugettext(u'Non')))
        # below, see here for an explanation
        # https://github.com/brutasse/django-floppyforms/issues/52
        Select.__init__(self, attrs, choices)


class MapWidget(Input):
    """
    Abstract Map polygon widget

    """
    def __init__(self, *args, **kwargs):
        self.ads = kwargs.get('ads', None)
        self.strokeColor = kwargs.get('strokeColor', '#FF0000')
        self.fillColor = kwargs.get('fillColor', '#00FF00')
        self.lat = kwargs.get('lat', 48.856)
        self.lng = kwargs.get('lng', 2.333)
        super(MapWidget, self).__init__()

    def get_context_data(self):
        ctx = super(MapWidget, self).get_context_data()
        ctx['ads'] = self.ads
        ctx['fillColor'] = self.fillColor
        ctx['strokeColor'] = self.strokeColor
        ctx['lat'] = self.lat
        ctx['lng'] = self.lng
        return ctx

    class Media:
        js = (
            'geoads/js/poly_utils.js',
        )


class GooglePolygonWidget(MapWidget):
    """
    Map polygon widget (using Google map api v3)

    """
    template_name = 'floppyforms/gis/poly_google.html'

    class Media:
        js = (
            'http://maps.googleapis.com/maps/api/js?sensor=false&amp;libraries=drawing',
            'geoads/js/poly_googlemap.js',
        )


class LeafletWidget(MapWidget):
    """
    Map polygon widget (using OpenStreetMap)

    """
    template_name = 'floppyforms/gis/poly_leaflet.html'

    class Media:
        js = (
            'http://cdn.leafletjs.com/leaflet-0.4/leaflet.js',
            'geoads/js/poly_leaflet.js',
            'geoads/Leaflet.draw/leaflet.draw.js'
        )
        css = {
            'all': (
                'http://cdn.leafletjs.com/leaflet-0.4/leaflet.css',
                'geoads/Leaflet.draw/leaflet.draw.css'
            )
        }


class BooleanExtendedNumberInput(NumberInput):
    template_name = 'floppyforms/boolean_extended_number_input.html'
    # we should add jquery, but it's on all site pages so ...


class BooleanExtendedInput(Input):
    template_name = 'floppyforms/boolean_extended_input.html'


class SpecificRangeWidget(forms.MultiWidget):
    """
    Specific Range Widget, a range widget with min and max inputs

    """

    def __init__(self, attrs=None):
        widgets = (forms.TextInput(attrs={'placeholder': 'min', 'class': 'input-mini'}),
                   forms.TextInput(attrs={'placeholder': 'max', 'class': 'input-mini'}))
        super(SpecificRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u' - '.join(rendered_widgets)
