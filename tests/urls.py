from django.conf.urls.defaults import patterns, url

from geoads.views import (AdSearchView, AdDetailView,
    AdSearchDeleteView, AdCreateView,  AdUpdateView,
    CompleteView, AdDeleteView)

from tests.customads.models import TestAd
from tests.customads.forms import TestAdForm


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)$', AdDetailView.as_view(model=TestAd),
        name="view"),
    url(r'^search/$', AdSearchView.as_view(model=TestAd), name='search'),
    url(r'^search/(?P<search_id>\d+)/$', AdSearchView.as_view(model=TestAd),
        name='search'),
    url(r'^delete_search/(?P<pk>\d+)$', AdSearchDeleteView.as_view(),
        name='delete_search'),
    url(r'^add/$', AdCreateView.as_view(model=TestAd,
        form_class=TestAdForm), name='add'),
    url(r'^add/complete/$', CompleteView.as_view(), name='complete'),
    url(r'^(?P<pk>\d+)/edit$', AdUpdateView.as_view(model=TestAd,
        form_class=TestAdForm), name='edit'),
    url(r'^(?P<pk>\d+)/delete$', AdDeleteView.as_view(model=TestAd),
        name='delete'),
)
