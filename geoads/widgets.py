# coding=utf-8
""" ads widgets """

from django import forms
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext

from floppyforms.widgets import Input, NumberInput
import floppyforms


class ImageWidget(forms.FileInput):
    """
    Image widget
    Used for rendering ImagieField in Ad form
    """
    template = '%(input)s<br /><a href="%(image)s" target="_blank"><img src="%(image_thumbnail)s" /></a>'

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
                                      'image_thumbnail': value.thumbnail.url()}
        else:
            output = input_html
        return mark_safe(output)


class Select(floppyforms.Select, Input):
    template_name = 'floppyforms/select.html'

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        #just because of the line below, we need to not CHAIN
        #choices = chain(self.choices, choices)
        final_choices = []
        for option_value, option_label in choices:
            final_choices.append((force_unicode(option_value), option_label))
        extra = {'choices': final_choices}
        return Input.render(self, name, value, attrs=attrs,
                            extra_context=extra)


class IndifferentNullBooleanSelect(floppyforms.NullBooleanSelect, Select):
    """
    Select widget for use with null boolean select field
    """
    def render(self, name, value, attrs=None, choices=()):
        choices = ((u'1', ugettext(u'Indifférent')),
                   (u'2', ugettext('Yes')),
                   (u'3', ugettext('No')))
        try:
            value = {True: u'2', False: u'3', u'2': u'2', u'3': u'3'}[value]
        except KeyError:
            value = u'1'
        return Select.render(self, name, value, attrs, choices=choices)


class GooglePolygonWidget(Input):
    """
    Map polygon widget (using Google map api v3)
    """
    template_name = 'floppyforms/gis/poly_google.html'
    def __init__(self, *args, **kwargs):
        self.ads = kwargs.get('ads', None)
        self.search = kwargs.get('search', False)
        self.strokeColor = kwargs.get('strokeColor', '#FF0000')
        self.fillColor = kwargs.get('fillColor', '#00FF00')
        self.lat = kwargs.get('lat', 48.856)
        self.lng = kwargs.get('lng', 2.333)
        super(GooglePolygonWidget, self).__init__()
    def get_context_data(self):
        ctx = super(GooglePolygonWidget, self).get_context_data()
        ctx['ads'] = self.ads
        ctx['search'] = self.search
        ctx['fillColor'] = self.fillColor
        ctx['strokeColor'] = self.strokeColor
        ctx['lat'] = self.lat
        ctx['lng'] = self.lng
        return ctx
    class Media:
        js = (
            'http://maps.googleapis.com/maps/api/js?sensor=false&amp;libraries=drawing',
            'js/poly_googlemap.js',
        )

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
        widgets = (forms.TextInput(attrs={'placeholder':'min'}), 
                   forms.TextInput(attrs={'placeholder':'max'}))
        super(SpecificRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u' - '.join(rendered_widgets)