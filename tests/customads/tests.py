# coding=utf-8
"""
GeoAd test module

All test are done synchronously in tests (as python-rq is allready tested)
"""
from django.test import TransactionTestCase, TestCase
from django.test.client import RequestFactory
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from mock_django import mock_signal_receiver

from geoads import views
from geoads.filtersets import AdFilterSet
from geoads.models import AdSearch
from geoads.filters import BooleanForNumberFilter
from geoads.models import Ad
from geoads.utils import geocode

from customads.models import TestAd, TestNumberAd
from customads.forms import TestAdForm
from customads.factories import UserFactory, TestAdFactory, TestNumberAdFactory, TestAdSearchFactory, TestModeratedAdFactory
from customads.filtersets import TestAdFilterSet

from geoads.signals import (geoad_new_interested_user, geoad_new_relevant_ad_for_search, geoad_post_save_ended)

from geoads.contrib.moderation.signals import moderation_in_progress


class GeoadsBaseTestCase(TransactionTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        
class AdDeleteViewTestCase(GeoadsBaseTestCase):

    def test_owner_delete(self):
        # Create an ad
        # Test if owner can delete it
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
        self.assertFalse(test_ad in TestAd.objects.all())

    def test_not_owner_delete(self):
        # Create a user and an ad
        # Test if the user who is not the ad owner can't delete it
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
        self.assertTrue(test_ad in TestAd.objects.all())


class AdUpdateViewTestCase(GeoadsBaseTestCase):

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


class AdSearchAndMoreViewTestCase(GeoadsBaseTestCase):

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


class AdDetailViewTestCase(GeoadsBaseTestCase):

    def test_read(self):
        test_ad = TestAdFactory.create()
        request = self.factory.get('/')
        response = views.AdDetailView.as_view(model=TestAd)(request, pk=test_ad.pk)

    #def test_send_message(self):
    #    test_ad = TestAdFactory.create()
    #    user = UserFactory.create()
    #    request = self.factory.post('/', data={'message': 'Hi buddy !'})
    #    request.user = user
    #    response = views.AdDetailView.as_view(model=TestAd)(request, pk=test_ad.pk)


class AdCreateViewTestCase(GeoadsBaseTestCase):

    def test_create(self):
        # get form
        request = self.factory.get('/')
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # valid
        form_data = {'brand': 'my_guitar',
                     'user_entered_address': '5 rue de Verneuil, Paris',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        # invalid
        form_data = {'brand': 'my_guitar',
                     'user_entered_address': 'fkjfkjfkjfkj',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        user = UserFactory.create()
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)
        self.assertEqual(response.context_data['form'].errors['user_entered_address'], [u'Indiquer une adresse valide.'])

    def test_create_same_slug(self):
        user = UserFactory.create()
        form_data = {'brand': 'my_guitar',
                     'user_entered_address': '5 rue de Verneuil, Paris',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)

        form_data = {'brand': 'my_guitar',
                     'user_entered_address': '5 rue de Verneuil, Paris',
                     'geoads-adpicture-content_type-object_id-TOTAL_FORMS': 4,
                     'geoads-adpicture-content_type-object_id-INITIAL_FORMS': 0}
        request = self.factory.post('/', data=form_data, files=[])
        request.user = user
        response = views.AdCreateView.as_view(model=TestAd, form_class=TestAdForm)(request)


class AdPotentialBuyersViewTestCase(GeoadsBaseTestCase):

    def test_view(self):
        # create ad and an adsearch
        adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                              content_type=ContentType.objects.get_for_model(TestAd),
                                              public=True)
        ad = TestAdFactory.create(brand="myfunkybrand")
        request = self.factory.get('/')
        request.user = ad.user
        response = views.AdPotentialBuyersView.as_view(model=TestAd)(request, pk=ad.id)
        self.assertEqual(response.context_data['object'], ad)
        self.assertEqual(response.context_data['object_list'][0], adsearch.adsearchresult_set.all()[0])


class AdPotentialBuyerContactViewTestCase(GeoadsBaseTestCase):

    def test_view(self):
        # create ad and an adsearch
        adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                              content_type=ContentType.objects.get_for_model(TestAd),
                                              public=True)
        ad = TestAdFactory.create(brand="myfunkybrand")
        request = self.factory.get('/')
        request.user = ad.user
        response = views.AdPotentialBuyerContactView.as_view()(request,
                adsearchresult_id=adsearch.adsearchresult_set.all()[0])
        request = self.factory.post('/', data={'message': 'I love your ad'}, files=[])
        request.user = ad.user
        response = views.AdPotentialBuyerContactView.as_view()(request,
                adsearchresult_id=adsearch.adsearchresult_set.all()[0])


class UtilsFiltersTestCase(GeoadsBaseTestCase):

    def test_booleanfornumberfilter(self):
        tbads = TestNumberAdFactory.create_batch(20)
        bfnf = BooleanForNumberFilter(name='number')
        qs = TestNumberAd.objects.all()
        self.assertEqual(qs, bfnf.filter(qs, None))
        self.assertEqual(bfnf.filter(qs, True).count(), TestNumberAd.objects.filter(number__isnull=False).count())
        TestNumberAd.objects.all().delete()


class FiltersetsTestCase(GeoadsBaseTestCase):

    def test_filterset(self):
        ad = TestAdFactory.create(brand="myfunkybrand")
        filterset = TestAdFilterSet({'brand': 'myfunkybrand'})
        self.assertEquals(len(filterset), 1)
        self.assertEquals(filterset[0], ad)
        ad.delete()


class ModelsTestCase(GeoadsBaseTestCase):

    def test_model_without_get_full_description(self):
        """
        Test that a model which inherit from Ad base model
        define a get_full_description method,
        otherwise it will raise a NotImplementedError
        """
        class BadAd(Ad):
            pass
        ba = BadAd()
        self.assertRaises(NotImplementedError, ba.get_full_description)


class UtilsTestCase(GeoadsBaseTestCase):

    def test_geocode(self):
        geo = geocode('13 place d\'Aligre Paris')
        self.assertTrue('address' in geo)
        self.assertTrue('location' in geo)



class GeoadsSignalsTestCase(GeoadsBaseTestCase):

    def test_ad_adsearch_and_ads_signals_1(self):
        """
        Test if signals are well sent to the buyer and the seller
        in case the search is created before the ad
        and initially with public set to True
        """
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=True)
                ad = TestAdFactory.create(brand="myfunkybrand")
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                adsearch.delete()
                ad.delete()

    def test_ad_adsearch_and_ads_signals_2(self):
        """
        Test if signals are well sent to the buyer and the seller
        in case the search is created before the ad
        and initially with public set to False, and in a second time set to True
        """
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=False)
                ad = TestAdFactory.create(brand="myfunkybrand")
                self.assertEquals(receiver_buyer.call_count, 1)
                adsearch.public = True
                adsearch.save()
                self.assertEquals(receiver_vendor.call_count, 1)
                adsearch.delete()
                ad.delete()

    def test_ad_adsearch_and_ads_signals_3(self):
        """
        Test if signals are well sent to the buyer and the seller
        in case the search is created after the ad
        and initially with public set to True
        """
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                ad = TestAdFactory.create(brand="myfunkybrand")
                adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=True)
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                adsearch.delete()
                ad.delete()

    def test_ad_adsearch_and_ads_signals_4(self):
        """
        Test if signals are well sent to the buyer and the seller
        in case the search is created after the ad
        and initially with public set to False and in a second time set to True
        """
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                ad = TestAdFactory.create(brand="myfunkybrand")
                adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=False)
                self.assertEquals(receiver_buyer.call_count, 1)
                adsearch.public = True
                adsearch.save()
                self.assertEquals(receiver_vendor.call_count, 1)
                adsearch.delete()
                ad.delete()

    def test_ad_adsearch_and_ads_signals_5(self):
        """
        Mixed case where we change the different fields of ad and addsearch
        """
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                ad = TestAdFactory.create(brand="myfunkybrand")
                adsearch = TestAdSearchFactory.create(search="brand=mytoofunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=True)

                self.assertEquals(receiver_buyer.call_count, 0)
                self.assertEquals(receiver_vendor.call_count, 0)
                # modify Ad to correspond => signal to buyer
                ad.brand = "mytoofunkybrand"
                ad.save()
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                # resave Ad to be sure, signal isn't send one more time
                ad.brand = "mytoofunkybrand"
                ad.save()
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                # modify AdSearch to not correspond
                adsearch.search = "brand=myfunkybrand"
                adsearch.save()
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                # modify AdSearch to corresond => mail to both
                ad.brand = "myfunkybrand"
                ad.save()
                self.assertEquals(receiver_buyer.call_count, 2)
                self.assertEquals(receiver_vendor.call_count, 2)
                # just change the Ad description to be sure signal is not sent another time
                ad.description = "you must buy it"
                ad.save()
                self.assertEquals(receiver_buyer.call_count, 2)
                self.assertEquals(receiver_vendor.call_count, 2)
                adsearch.delete()
                ad.delete()

    def test_remove_ad_from_ad_search(self):
        with mock_signal_receiver(geoad_new_relevant_ad_for_search) as receiver_buyer:
            with mock_signal_receiver(geoad_new_interested_user) as receiver_vendor:
                adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                                      content_type=ContentType.objects.get_for_model(TestAd),
                                                      public=True)
                ad = TestAdFactory.create(brand="myfunkybrand")
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                # modify Ad to correspond => signal to buyer
                ad.brand = "mytoofunkybrand"
                ad.save()
                self.assertEquals(receiver_buyer.call_count, 1)
                self.assertEquals(receiver_vendor.call_count, 1)
                adsearch.delete()
                ad.delete()

    def test_ad_search_result_remove(self):
        ad = TestAdFactory.create(brand="myfunkybrand")
        adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                              content_type=ContentType.objects.get_for_model(TestAd),
                                              public=True)
        ad.brand = "mytoofunkybrand"
        ad.save()
        ad.delete()
        adsearch.delete()


class AdModelPropertyTestCase(TestCase):

    def test_ad_model_property(self):
        ad = TestAdFactory.create(brand="myfunkybrand")
        adsearch = TestAdSearchFactory.create(search="brand=myfunkybrand",
                                              content_type=ContentType.objects.get_for_model(TestAd),
                                              public=True)
        self.assertEqual(ad.public_adsearch, [adsearch, ])
        adsearch.public = False
        adsearch.save()
        self.assertEqual(ad.public_adsearch, [])


class GeoadsModerationTestCase(TestCase):

    def test_ad_creation(self):
        # We test that before and after moderation, correct event is sent
        # Before moderation, it's moderation_in_progress
        # After moderation, it's the same case as ad would have been saved: 
        # so we track geoad_post_save_ended signals
        with mock_signal_receiver(geoad_post_save_ended) as save_ended:
            with mock_signal_receiver(moderation_in_progress) as mod_in_progress:
                ad = TestModeratedAdFactory(brand="myfunkybrand")
                self.assertEquals(mod_in_progress.call_count, 1)
                self.assertEquals(save_ended.call_count, 0)
                ad.moderated_object.approve()
                self.assertEquals(mod_in_progress.call_count, 1)
                self.assertEquals(save_ended.call_count, 1)

