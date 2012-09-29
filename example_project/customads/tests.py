# coding=utf-8
"""
GeoAd test module

"""

from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType

from geoads import views
from geoads.filtersets import AdFilterSet
from geoads.models import AdSearch
from geoads.forms import BaseAdForm
from geoads.filters import BooleanForNumberFilter
from geoads.templatetags.ads_tag import priceformat

from customads.models import TestAd, TestBooleanAd
from customads.forms import TestAdForm
from customads.factories import UserFactory, TestAdFactory, TestBooleanAdFactory, TestAdSearchFactory
# UGLY UGLY UGLY fucking hack, I need to import this
# to be sure that my hook to set filterset on model instance
# will be available
from customads.filtersets import TestAdFilterSet
#from geoads.models import Ad
from geoads.signals import *


class AdDeleteViewTestCase(unittest.TestCase):

    def setUp(self):
        # set up request factory
        self.factory = RequestFactory()

    def test_owner_delete(self):
        # create an ad and test if owner can delete it
        test_ad = TestAdFactory.create()
        request = self.factory.get('/')
        request.user = test_ad.user
        response = views.AdDeleteView.as_view(model=TestAd)(request, pk=test_ad.pk)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post('/')
        request.user = test_ad.user
        response = views.AdDeleteView.as_view(model=TestAd)(request, pk=test_ad.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(TestAd.DoesNotExist, TestAd.objects.get, id=test_ad.id)

    def test_not_owner_delete(self):
        # create a user, and an ad, and test if the user
        # who is not the ad owner can't delete it
        test_ad = TestAdFactory.create()
        user = UserFactory.create()
        request = self.factory.get('/')
        request.user = user
        view = views.AdDeleteView.as_view(model=TestAd)
        self.assertRaises(Http404, view, request, pk=test_ad.pk)
        request = self.factory.post('/')
        request.user = user
        view = views.AdDeleteView.as_view(model=TestAd)
        self.assertRaises(Http404, view, request, pk=test_ad.pk)


class AdUpdateViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_owner_update(self):
        test_ad = TestAdFactory.create()
        form_data = {
            'brand': test_ad.brand,
            'location': test_ad.location,
            'user_entered_address': test_ad.user_entered_address,
            'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
            'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.get('/')
        request.user = test_ad.user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=test_ad.pk)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post('/', data=form_data)
        request.user = test_ad.user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=test_ad.pk)
        self.assertEqual(response.status_code, 301)

    def test_not_owner_update(self):
        test_ad = TestAdFactory.create()
        user = UserFactory.create()
        form_data = {
            'brand': test_ad.brand,
            'location': test_ad.location,
            'user_entered_address': test_ad.user_entered_address,
            'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
            'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.get('/')
        request.user = user
        view = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)
        self.assertRaises(Http404, view, request, pk=test_ad.pk)
        request = self.factory.post('/', data=form_data)
        request.user = user
        view = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)
        self.assertRaises(Http404, view, request, pk=test_ad.pk)
        #self.assertEqual(response.status_code, 301)


class AdSearchAndMoreViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_home_adsearchview(self):
        # client just get the adsearchview
        TestAdFactory.create_batch(12)
        request = self.factory.get('/')
        response = views.AdSearchView.as_view(model=TestAd)(request)
        self.assertEqual(response.status_code, 200)
        # check that we set initial_ads
        self.assertTrue('initial_ads' in response.context_data)
        # check that ad_search_form is None
        # so that user can't save initial search
        self.assertTrue('ad_search_form' not in response.context_data)
        # check that filter is instance of AdFilterSet
        self.assertTrue(isinstance(response.context_data['filter'], AdFilterSet))

    def test_filterads(self):
        test_ads = TestAdFactory.create_batch(12)
        # client try to filter search
        # and get at lead one result
        request = self.factory.get('/', data={'brand': test_ads[0].brand})
        user = UserFactory.create()
        request.user = user
        response = views.AdSearchView.as_view(model=TestAd)(request)
        # check that we don't return initial ads
        self.assertTrue('initial_ads' not in response.context_data)
        # check that the user have a form to save it search
        self.assertTrue('ad_search_form' in response.context_data)
        # or get 0 results
        request = self.factory.get('/', data={'brand': 'nologo'})
        request.user = user
        response = views.AdSearchView.as_view(model=TestAd)(request)


    def test_create_update_read__delete_search(self):
        test_ad = TestAdFactory.create()
        # here we build a search ad form
        # create
        location = "SRID%3D900913%3BPOLYGON((2.3886182861327825+48.834761790252024%2C2.2773817138671575+48.837925498723266%2C2.3251035766601262+48.87180983721773%2C2.4023511962890325+48.87293892019383%2C2.3886182861327825+48.834761790252024))"
        request = self.factory.post('/', data={'search': 'brand=' + test_ad.brand + '&location=' + location})
        user = UserFactory.create()
        request.user = user
        response = views.AdSearchView.as_view(model=TestAd)(request)
        ad_search = AdSearch.objects.all().filter(user=user)[0]
        # update
        request = self.factory.post('/', data={'search': 'brand=' + test_ad.brand})
        request.user = user
        response = views.AdSearchView.as_view(model=TestAd)(request, search_id=ad_search.pk)
        # read
        request = self.factory.get('/')
        request.user = user
        response = views.AdSearchView.as_view(model=TestAd)(request, search_id=ad_search.pk)
        not_ad_search_owner_user = UserFactory.create()
        request = self.factory.get('/')
        request.user = not_ad_search_owner_user
        view = views.AdSearchView.as_view(model=TestAd)
        self.assertRaises(Http404, view, request, search_id=ad_search.pk)
        # delete
        request = self.factory.get('/')
        # by non authorized user
        request.user = not_ad_search_owner_user
        view = views.AdSearchDeleteView.as_view()
        self.assertRaises(Http404, view, request, pk=ad_search.pk)
        # by authorized user (owner of ad search)
        request = self.factory.post('/')
        request.user = ad_search.user
        response = views.AdSearchDeleteView.as_view()(request, pk=ad_search.pk)


class AdDetailViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_read(self):
        test_ad = TestAdFactory.create()
        request = self.factory.get('/')
        response = views.AdDetailView.as_view(model=TestAd)(request, pk=test_ad.pk)

    def test_send_message(self):
        test_ad = TestAdFactory.create()
        user = UserFactory.create()
        request = self.factory.post('/', data={'message':'Hi buddy !'})
        request.user = user
        response = views.AdDetailView.as_view(model=TestAd)(request, pk=test_ad.pk)


class AdCreateViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_create(self):
        # get form
        request = self.factory.get('/')
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # valid
        form_data = {'brand': 'my_guitar',
            'user_entered_address': '5 rue de Vernueil, Paris',
            'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
            'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # invalid
        form_data = {'brand': 'my_guitar',
            'user_entered_address': 'fkjfkjfkjfkjf',
            'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
            'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        self.assertEqual(response.context_data['form'].errors['user_entered_address'], [u'Indiquer une adresse valide.'])


class UtilsFiltersTestCase(unittest.TestCase):

    def test_booleanfornumberfilter(self):
        tbads = TestBooleanAdFactory.create_batch(20)
        bfnf = BooleanForNumberFilter(name='boolean')
        qs = TestBooleanAd.objects.all()
        #self.assertEqual(qs, bfnf.filter(qs, None))
        #self.assertEqual(bfnf.filter(qs, True).count(), TestBooleanAd.objects.filter(boolean=True).count())


class GeoadsSignalsTestCase(unittest.TestCase):

    def test_adsignal(self):
        # first, we clear all datas
        TestAd.objects.all().delete()
        AdSearch.objects.all().delete()
        #test_ad = TestAdFactory.create()
        # here we create an AdSearch that should hold all ads
        test_adsearch = TestAdSearchFactory.create(content_type=ContentType.objects.get_for_model(TestAd))
        # here we create an Ad, and should then get it inside AdSearchResult of test_adsearch
        test_ad = TestAdFactory.create()
        self.assertEqual(test_adsearch.adsearchresult_set.all().count(), 1)
        test_adsearch.search = "brand=myfunkybrand"
        test_adsearch.save()
        self.assertEqual(test_adsearch.adsearchresult_set.all().count(), 0)
        test_adsearch.search = "brand=%s" % (test_ad.brand)
        test_adsearch.save()
        self.assertEqual(test_adsearch.adsearchresult_set.all().count(), 1)
        test_ad.brand = "newbrandnameduetofuckingmarketingservice"
        test_ad.save()
        self.assertEqual(test_adsearch.adsearchresult_set.all().count(), 0)


class GeoadsTemplateTagsTestCase(unittest.TestCase):

    def test_priceformat(self):
        self.assertEqual(priceformat('3000'), '3 000')
