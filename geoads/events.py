#-*- coding: utf-8 -*-
"""
Ads app events module

2 things here:
- a signal connector from all subclasses
- events used to bound Ad and AdSearch/AdSearchResult models
"""
import logging

from django_rq import job

from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType

from .models import AdSearchResult, AdSearch, Ad
from .signals import (geoad_new_interested_user, geoad_post_save_ended,
                            geoad_new_relevant_ad_for_search)


logger = logging.getLogger(__name__)


@job
def async_post_save_handler(instance):
    # we must test and do 2 things
    # remove the ad to adsearch it doesn't more belongs to
    ct = ContentType.objects.get_for_model(instance)
    q1 = AdSearch.objects.filter(adsearchresult__object_pk=instance.pk,
                                 adsearchresult__content_type=ct)
    for ad_search in q1:
        query = QueryDict(ad_search.search)
        filter = ad_search.content_type.model_class().filterset()(query or None)
        if instance not in filter.qs:
            ad_search_result = AdSearchResult.objects.get(ad_search=ad_search, object_pk=instance.pk,
                                                          content_type=ct)
            ad_search_result.delete()
    # add the ad to adsearch it belongs to
    q2 = AdSearch.objects.exclude(adsearchresult__object_pk=instance.pk,
                                  adsearchresult__content_type=ct)
    for ad_search in q2:
        query = QueryDict(ad_search.search)
        filter = ad_search.content_type.model_class().filterset()(query or None)
        if instance in filter.qs:
            # here we do a get_or_create, in case the add, even modified
            # is always inside the search
            adr, created = AdSearchResult.objects.get_or_create(ad_search=ad_search, object_pk=instance.pk,
                           content_type=ContentType.objects.get_for_model(instance))
            #logger.info('>>>>>> %s %s' % (adr, created))
    geoad_post_save_ended.send(sender=Ad, ad=instance)


def ad_post_save_handler(sender, instance, **kwargs):
    async_post_save_handler.delay(instance)


def ad_search_post_save_handler(sender, instance, created, **kwargs):
    # this should be optimized if search field is modified !
    # if it's only other conf file, we should'nt test for new/remove ads
    q = QueryDict(instance.search)
    filter = instance.content_type.model_class().filterset()(q or None)
    # here we remove ads that no more belongs to AdSearch
    ads = AdSearchResult.objects.filter(ad_search=instance)
    for ad in ads:
        if ad.content_object not in filter.qs:
            ad.delete()
    # here we save search AdSearchResult instances
    # so we add an Ad if it belongs to AdSearch
    for ad in filter.qs:
        ad_search_result, created = AdSearchResult.objects.get_or_create(
            ad_search=instance,
            content_type=instance.content_type,
            object_pk=ad.id)
        # this below shoud help in case, ad_search change from not public to public
        # and we want to inform vendor that someone is interested in its ad
        #ad_search_result.save()


def ad_search_result_post_save_handler(sender, instance, created, **kwargs):
    if created:
        geoad_new_relevant_ad_for_search.send(sender=Ad, ad=instance.content_object, relevant_search=instance)
        if instance.ad_search.public:
            geoad_new_interested_user.send(sender=Ad, ad=instance.content_object, interested_user=instance.ad_search.user)
