from django.conf.urls import patterns, url
from geoads.views import (AdSearchView, AdDetailView, AdSearchDeleteView,
                          AdCreateView,  AdUpdateView, CompleteView, AdDeleteView, 
                          AdPotentialBuyersView, AdPotentialBuyerContactView)
from geoads.models import AdSearchResult
from tests.customads.models import TestAd
from tests.customads.forms import TestAdForm
# this import below, unused, is to instantiate the filter with metaclass and set the model filterset var
from tests.customads.filtersets import TestAdFilterSet

from moderation.helpers import auto_discover
auto_discover()


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)$', AdDetailView.as_view(model=TestAd), name="view"),
    url(r'^search/$', AdSearchView.as_view(model=TestAd), name='search'),
    url(r'^search/(?P<search_id>\d+)/$', AdSearchView.as_view(model=TestAd), name='search'),
    url(r'^delete_search/(?P<pk>\d+)$', AdSearchDeleteView.as_view(), name='delete_search'),
    url(r'^add/$', AdCreateView.as_view(model=TestAd, form_class=TestAdForm), name='add'),
    url(r'^add/complete/$', CompleteView.as_view(), name='complete'),
    url(r'^(?P<pk>\d+)/edit$', AdUpdateView.as_view(model=TestAd, form_class=TestAdForm), name='edit'),
    url(r'^(?P<pk>\d+)/delete$', AdDeleteView.as_view(model=TestAd), name='delete'),
    url(r'^contact_buyers/(?P<pk>\d+)$', AdPotentialBuyersView.as_view(model=TestAd), name="contact_buyers"),
    url(r'^contact_buyer/(?P<adsearchresult_id>\d+)$', AdPotentialBuyerContactView.as_view(), name="contact_buyer"),
)
