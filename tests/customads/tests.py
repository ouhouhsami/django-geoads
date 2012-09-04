# coding=utf-8
""" ads test module"""

from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.http import HttpRequest, Http404

from moderation.helpers import auto_discover

from customads.models import TestAd
from customads.filtersets import TestAdFilterSet
from customads.forms import TestAdForm
from geoads import views


class AdViewsTestCase(unittest.TestCase):
    # basic test for ad generic views

    def setUp(self):
        # ad moderation manager to our moderated model
        auto_discover()
        # set up request factory
        self.factory = RequestFactory()

    def test_get_adsearchview(self):
        # client just get the adsearchview
        request = self.factory.get('/')
        response = views.AdSearchView.as_view(model=TestAd,
                                      filterset_class=TestAdFilterSet)(request)
        self.assertEqual(response.status_code, 200)
        # at first time client get search view, and doesn't search ads
        self.assertEqual(response.context_data['search'], False)
        # check that we set initial_ads
        self.assertTrue('initial_ads' in response.context_data)


    def test_post_adsearchview(self):
        request = self.factory.post('/')
        # pb if not logged; pb of message for anonymous user
        # even if message for anonymous user are set !
        request.user = User.objects.get(username="paul")
        response = views.AdSearchView.as_view(model=TestAd, 
                                      filterset_class=TestAdFilterSet)(request)
        ads = TestAd.objects.all()
        #print ads
        #print ads[0].visible
        #print response.context_data['filter'].form, 'jljk'
        #print response.context_data['filter'].qs
        self.assertTrue(response.context_data['search'])


    def test_adcreateview(self):
        # init 
        request = self.factory.get('/ad/create')
        user = User.objects.create_user('paul', 'maccartney@thebeatles.com', 
                                                                'paulpassword')
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd)(request)
        
        # can reach ad create view
        self.assertEqual(response.status_code, 200)
        
        # be sure that picture formset is available
        self.assertTrue('picture_formset' in response.context_data)
        
        # post without filling form/data
        request = self.factory.post('/ad/create')
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        self.assertEqual(response.status_code, 200)
        # form is invalid
        self.assertEqual(response.context_data['form'].is_valid(), False)
        
        # post with a good datas
        form_data = {'slug':'my_awesome_ad', 
                     'user_entered_address':'5 rue de Vernueil, Paris', 
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS':4, 
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS':0}
        request = self.factory.post('/ad/create', data=form_data, files=[])
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # redirect after valid form
        self.assertEqual(response.status_code, 301)

        # post with wrong datas
        form_data = {'slug':'my_awesome_ad', 
                     'user_entered_address':'foo bar', 
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS':4, 
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS':0}
        request = self.factory.post('/ad/create', data=form_data, files=[])
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # return to form edition view to correct address
        self.assertEqual(response.status_code, 200)
        

    def test_adreadview(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 
                                                                'johnpassword')
        test_ad, created = TestAd.objects.get_or_create(user=user, 
                     user_entered_address="13 place d'Aligre Paris", slug="1",
                     location="POINT (2.3479424000000000 48.8714721999999995)")
        test_ad.save()
        request = self.factory.get('/ad/read/1')
        # here ad is pending => we shouldn't be able to read it 
        view = views.AdDetailView.as_view(model=TestAd)
        self.assertRaises(Http404, view, request, slug="1")
        # here ad is approved => we shoud be able to view it
        test_ad.moderated_object.approve()
        response = view(request, slug="1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['ad'], test_ad)
        # here consumer tries to send a mail to ad owner
        # TODO: test if user not logged
        consumer = User.objects.create_user('con', 'con@sumer.com', 
                                                                'conpassword')
        form_data = {'message':'hi buddy'}
        request = self.factory.post('/ad/read/1', data=form_data)
        request.user = consumer
        response = views.AdDetailView.as_view(model=TestAd)(request, slug="1")
        self.assertEqual(response.status_code, 200)

    def test_adupdateview(self):
        ad = TestAd.objects.get(slug="1")
        user = User.objects.get(username='john')
        # with a valid form
        form_data = {'slug':'1', 
                     'user_entered_address':'14 place d\'Aligre Paris', 
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS':4, 
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS':0}        
        request = self.factory.post('/ad/update/1', data=form_data)
        request.user = user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=3)
        self.assertEqual(response.status_code, 301)
        # with an invalid form
        form_data = {'slug':'1', 
                     'user_entered_address':'flkdqjfkljqlfkjlk', 
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS':4, 
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS':0}        
        request = self.factory.post('/ad/update/1', data=form_data)
        request.user = user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=3)
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/ad/update/1')
        request.user = user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=3)
        self.assertEqual(response.status_code, 200)

        # non-owner user can update ad
        other_user = User.objects.get(username='paul')
        request = self.factory.get('/ad/update/1', data=form_data)
        request.user = other_user
        view = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)
        self.assertRaises(Http404, view, request, pk=3)
        #self.assertEqual(response.status_code, 200)

    def test_addeleteview(self):
        user = User.objects.create_user('mike', 'jagger@therollingstones.com', 
                                                                'mikepassword')
        test_ad, created = TestAd.objects.get_or_create(user=user, 
                     user_entered_address="1 rue refaite Paris", slug="jhome",
                     location="POINT (2.3479424000000000 48.8714721999999995)")
        test_ad.save()
        test_ad.moderated_object.approve()
        # here I need to set the pl value, but how, it's in url
        request = self.factory.get('/ad/delete/1')
        request.user = user
        response = views.AdDeleteView.as_view(model=TestAd)(request, pk=2)
        request = self.factory.get('/ad/delete/1')
        request.user = User.objects.get(username='paul')
        self.assertRaises(Http404,  views.AdDeleteView.as_view(model=TestAd), 
                                                                request, pk=2)
        request = self.factory.post('/ad/delete/1')
        request.user = User.objects.get(username='mike')
        response = views.AdDeleteView.as_view(model=TestAd)(request, pk=2)
        