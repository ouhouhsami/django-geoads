from django.forms import ModelForm

from geoads.forms import BaseAdForm
from customads.models import TestAd


class TestAdForm(BaseAdForm):
    class Meta:
        model = TestAd
        exclude = ('user', 'delete_date', 'location', 'address')


class TestAdFilterSetForm(ModelForm):
    class Meta:
        model = TestAd
        exclude = ('user', 'delete_date', 'location', 'address')