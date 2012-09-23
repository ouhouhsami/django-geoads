# coding=utf-8
from django import forms
from django.forms import ModelForm
from django.contrib.gis.geos import Point

from pygeocoder import Geocoder, GeocoderError

from geoads.models import AdPicture, AdContact, AdSearch, AdSearchResult, Ad
from geoads.widgets import ImageWidget


class AdPictureForm(ModelForm):
    """
    Ad picture form
    Warning: just used for class based views in this app
    Applications could/should make it more pretty
    """
    image = forms.ImageField(widget=ImageWidget(), required=False)

    class Meta:
        model = AdPicture


class AdContactForm(ModelForm):
    """
    Ad contact form
    """
    class Meta:
        model = AdContact
        exclude = ['user', 'content_type', 'object_pk']


class AdSearchForm(ModelForm):
    """
    Ad search form
    """
    class Meta:
        model = AdSearch
        fields = ('search', )
        widgets = {
            'search': forms.HiddenInput
        }


class AdSearchResultContactForm(ModelForm):
    """
    Ad Search Result Contact Form
    """
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), required=False
        )

    class Meta:
        model = AdSearchResult
        fields = ('message', 'id')
        exclude = ('ad_search', 'content_type',
            'object_pk', 'create_date', 'contacted')


class AdSearchUpdateForm(ModelForm):
    """
    Ad search form for update
    """
    class Meta:
        model = AdSearch
        fields = ('public', 'description')


class BaseAdForm(ModelForm):
    """
    Base ad form
    Use it with your own Ad instance
    """

    def clean_user_entered_address(self):
        # here we try to figure if user entered address
        # is an existing address
        # ! of course, this will be needed an other time
        # to set address and location fields in ad model
        # don't know how to improve this for the moment
        # and just have it computed one time
        data = self.cleaned_data['user_entered_address']
        try:
            geocode = Geocoder.geocode(data.encode('ascii', 'ignore'))
            self.address = geocode.raw
            coordinates = geocode[0].coordinates
            pnt = Point(coordinates[1], coordinates[0], srid=900913)
            self.location = pnt
        except GeocoderError:
            raise forms.ValidationError(u"Indiquer une adresse valide")
        return data

    class Meta:
        model = Ad
        exclude = ('user', 'delete_date', 'location', 'address')
