from geoads.filtersets import AdFilterSet
from customads.models import TestAd
from customads.forms import TestAdFilterSetForm


class TestAdFilterSet(AdFilterSet):

    class Meta:
        model = TestAd
        form = TestAdFilterSetForm
        fields = ['brand', ]
