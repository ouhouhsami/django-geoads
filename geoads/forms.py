# coding=utf-8
""" Ads forms """

from django import forms
from django.forms import ModelForm
from django.contrib.gis.geos import Point

from pygeocoder import Geocoder, GeocoderError
from moderation.forms import BaseModeratedObjectForm

from geoads.models import AdPicture, AdContact
from geoads.widgets import ImageWidget

class AdPictureForm(ModelForm):
    """Ad picture form"""
    image = forms.ImageField(widget=ImageWidget(), required=False)
    class Meta:
        model = AdPicture

class AdContactForm(ModelForm):
    """Ad contact form"""
    class Meta:
        model = AdContact
        exclude = ['user', 'content_type', 'object_pk']

class BaseAdForm(BaseModeratedObjectForm, ModelForm):
    """Base ad form
    Use it with your own Ad instance
    """
    def clean(self):
        if self.cleaned_data.has_key('user_entered_address'):
            self.cleaned_data['address'] = self.address
            self.cleaned_data['location'] = self.location
        return self.cleaned_data

    def clean_user_entered_address(self):
        data = self.cleaned_data['user_entered_address']
        try:
            geocode = Geocoder.geocode(data.encode('ascii','ignore'))
            self.address = geocode.raw
            coordinates = geocode[0].coordinates
            pnt = Point(coordinates[1], coordinates[0], srid=900913)
            self.location = pnt
        except GeocoderError:
            raise forms.ValidationError(u"Indiquer une adresse valide")
        return data
    class Meta:
        exclude = ('user', 'delete_date', 'location', 'address')