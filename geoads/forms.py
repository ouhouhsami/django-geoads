#-*- coding: utf-8 -*-
"""
Ads app forms module

This module provides default forms to work with Ad, AdContact, AdSearch forms.
"""
from django import forms
from django.conf import settings
from django.http import QueryDict

from geoads.models import AdPicture, AdContact, AdSearch, AdSearchResult, Ad
from geoads.utils import geocode


class AdPictureForm(forms.ModelForm):
    """
    Ad picture form
    """
    image = forms.ImageField(required=False)

    class Meta:
        model = AdPicture


class AdContactForm(forms.ModelForm):
    """
    Ad contact form
    """
    class Meta:
        model = AdContact
        exclude = ['user', 'content_type', 'object_pk']


class AdSearchForm(forms.ModelForm):
    """
    Ad search form
    """

    def clean_search(self):
        # Remove all empty elements of search field
        # Django `QueryDict` uses keep_blank_values=True
        # in parse_qsl that keeps empty values as [u'']
        # which is not in our use case
        # Below, we remove these values, and only keep setted ones.
        data = self.cleaned_data['search']
        q = QueryDict(data, mutable=True)
        [q.pop(elt[0]) for elt in q.lists() if elt[1] == [u'']]
        return q.urlencode()

    class Meta:
        model = AdSearch
        fields = ('search', )
        widgets = {
            'search': forms.HiddenInput
        }


class AdSearchResultContactForm(forms.ModelForm):
    """
    Ad Search Result Contact Form
    """
    message = forms.CharField(label=u"Votre message à l'acheteur ",
        widget=forms.Textarea(attrs={'rows': 4}), required=False
        )

    class Meta:
        model = AdSearchResult
        fields = ('message', 'id')
        exclude = ('ad_search', 'content_type',
            'object_pk', 'create_date', 'contacted')


class AdSearchUpdateForm(forms.ModelForm):
    """
    Ad search form for update
    """
    class Meta:
        model = AdSearch
        fields = ('public', 'description')


class BaseAdForm(forms.ModelForm):
    """
    Base Ad form
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
        if settings.BYPASS_GEOCODE is True:
            if data == 'fkjfkjfkjfkj':  # hook to not use BYPASS_GEOCODE
                raise forms.ValidationError(u"Indiquer une adresse valide.")
            return data
        else:
            try:
                geocode(data.encode('ascii', 'ignore'))
            except:  # TODO: create GeocodeError
                raise forms.ValidationError(u"Indiquer une adresse valide.")
            return data

    class Meta:
        model = Ad
        exclude = ('user', 'delete_date', 'location', 'address')
