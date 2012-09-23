# coding=utf-8
"""
GeoAd test module

"""

from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.forms import ModelForm

from geoads import views
from geoads.filtersets import AdFilterSet
from geoads.models import AdSearch

from customads.models import TestAd
from customads.forms import TestAdForm, TestAdFilterSetForm
from customads.factories import UserFactory, TestAdFactory
# UGLY UGLY UGLY fucking hack, I need to import this
# to be sure that my hook to set filterset on model instance
# will be available
from customads.filtersets import TestAdFilterSet


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
        request = self.factory.post('/', data={'search': 'brand=' + test_ad.brand})
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
            'user_entered_address': '',
            'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
            'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)

'''

class AdSearchViewTestCase(unittest.TestCase):
    # basic test for ad generic views

    def setUp(self):
        # set up request factory
        self.factory = RequestFactory()
        #UserFactory.create_batch(10)
        #TestAdFactory.create()
    def test_home_adsearchview(self):
        # client just get the adsearchview
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
    def test_filter_ads(self):
        # client try to filter search
        TestAdFactory.create()
        TestAdFactory.create()
        request = self.factory.get('/?brand=foo')
        request.user = UserFactory.create()
        response = views.AdSearchView.as_view(model=TestAd)(request)
        # check that we don't return initial ads
        self.assertTrue('initial_ads' not in response.context_data)
        # check that the user have a form to save it search
        self.assertTrue('ad_search_form' in response.context_data)
    def test_post_adsearchview(self):
        pass
        #self.assertTrue(response.context_data['search'])
    def test_adcreateview(self):
        # client want to add an ad
        request = self.factory.get('/ad/create')
        user = User.objects.create_user('paul',
            'maccartney@thebeatles.com', 'paulpassword')
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
        form_data = {'brand': 'my_guitar',
                     'user_entered_address': '5 rue de Vernueil, Paris',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/ad/create', data=form_data, files=[])
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # redirect after valid form
        self.assertEqual(response.status_code, 301)
        # post with wrong datas
        form_data = {'slug': 'my_awesome_ad',
                     'user_entered_address': 'foo bar',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
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
        #self.assertRaises(Http404, view, request, slug="1")
        # here ad is approved => we shoud be able to view it
        #test_ad.moderated_object.approve()
        response = view(request, slug="1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['ad'], test_ad)
        # here consumer tries to send a mail to ad owner
        # TODO: test if user not logged
        consumer = User.objects.create_user('con', 'con@sumer.com',
                                                                'conpassword')
        form_data = {'message': 'hi buddy'}
        request = self.factory.post('/ad/read/1', data=form_data)
        request.user = consumer
        response = views.AdDetailView.as_view(model=TestAd)(request, slug="1")
        self.assertEqual(response.status_code, 200)

    def test_adupdateview(self):
        ad = TestAd.objects.get(slug="1")
        user = User.objects.get(username='john')
        # with a valid form
        form_data = {'slug': '1',
                     'user_entered_address': '14 place d\'Aligre Paris',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/ad/update/1', data=form_data)
        request.user = user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=3)
        self.assertEqual(response.status_code, 301)
        # with an invalid form
        form_data = {'slug': '1',
                     'user_entered_address': 'sdfsdfsdfsdfsdf',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/ad/update/1', data=form_data)
        request.user = user
        response = views.AdUpdateView.as_view(model=TestAd, form_class=TestAdForm)(request, pk=3)
        self.assertEqual(response.status_code, 301)

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
'''
