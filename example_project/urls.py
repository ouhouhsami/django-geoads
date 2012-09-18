"""
AcheterSansCom urls.py

"""
from django.conf.urls.defaults import patterns, url
from geoads.views import (AdSearchView, AdDetailView, AdSearchDeleteView,
    AdCreateView,  AdUpdateView, CompleteView, AdDeleteView)
from example_project.customads.models import TestAd
from example_project.customads.forms import TestAdForm
# this import below, unused, is to instantiate the filter with metaclass and set the model filterset var
from example_project.customads.filtersets import TestAdFilterSet


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)$', AdDetailView.as_view(model=TestAd), name="view"),
    url(r'^search/$', AdSearchView.as_view(model=TestAd), name='search'),
    url(r'^search/(?P<search_id>\d+)/$', AdSearchView.as_view(model=TestAd), name='search'),
    url(r'^delete_search/(?P<pk>\d+)$', AdSearchDeleteView.as_view(), name='delete_search'),
    url(r'^add/$', AdCreateView.as_view(model=TestAd, form_class=TestAdForm), name='add'),
    url(r'^add/complete/$', CompleteView.as_view(), name='complete'),
    url(r'^(?P<pk>\d+)/edit$', AdUpdateView.as_view(model=TestAd, form_class=TestAdForm), name='edit'),
    url(r'^(?P<pk>\d+)/delete$', AdDeleteView.as_view(model=TestAd), name='delete'),
)
