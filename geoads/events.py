#-*- coding: utf-8 -*-
"""
Ads app events module

2 things here:
- a signal connector from all subclasses
- events used to bound Ad and AdSearch/AdSearchResult models
"""
import logging

from django_rq import job

from geoads.models import AdSearchResult, AdSearch, Ad
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


from geoads.signals import (geoad_new_interested_user, geoad_post_save_ended,
                            geoad_new_relevant_ad_for_search)

logger = logging.getLogger(__name__)


def get_subclasses(classes, level=0):
    """
    Return the list of all subclasses given class (or list of classes) has.
    Inspired by this question:
    http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
    """
    # for convenience, only one class can can be accepted as argument
    # converting to list if this is the case
    if not isinstance(classes, list):
        classes = [classes]

    if level < len(classes):
        classes += classes[level].__subclasses__()
        return get_subclasses(classes, level + 1)
    else:
        return classes


def receiver_subclasses(signal, sender, dispatch_uid_prefix, **kwargs):
    """
    A decorator for connecting receivers and all receiver's subclasses to signals. Used by passing in the
    signal and keyword arguments to connect::

        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...
    """
    def _decorator(func):
        all_senders = get_subclasses(sender)
        #logging.info(all_senders)
        for snd in all_senders:
            signal.connect(func, sender=snd, dispatch_uid=dispatch_uid_prefix + '_' + snd.__name__, **kwargs)
        return func
    return _decorator


@job('default', async=settings.GEOADS_ASYNC)
def async_post_save_handler(instance):
    # we must test and do 2 things
    # remove the ad to adsearch it doesn't more belongs to
    ct = ContentType.objects.get_for_model(instance)
    q1 = AdSearch.objects.filter(adsearchresult__object_pk=instance.pk,
                                 adsearchresult__content_type=ct)
    #if q.count() == 0:
    #    logger.info('\tFor the moment, our Ad:%s doesn\'t belong to any of our AdSearch' % (instance))
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
            AdSearchResult(ad_search=ad_search, object_pk=instance.pk,
                           content_type=ContentType.objects.get_for_model(instance)).save()
    geoad_post_save_ended.send(sender=Ad, ad=instance)


@job('default', async=settings.GEOADS_ASYNC)
def async_post_save_created_handler(instance):
    # attach ad to adsearch it belongs
    ct = ContentType.objects.get_for_model(instance)
    ad_searches = AdSearch.objects.filter(content_type=ct)
    for ad_search in ad_searches:
        q = QueryDict(ad_search.search)
        filter = ad_search.content_type.model_class().filterset()(q or None)
        if instance in filter.qs:
            AdSearchResult(ad_search=ad_search, object_pk=instance.pk,
                           content_type=ct).save()


def ad_post_save_handler(sender, instance, created, **kwargs):
    # We should test pre_save post => if it doesn't change => don't update ! don't do anything !
    # may be same thing for search
    # and quasi sure, test must be on the pre_save, not post_save !
    # for update without changing anything, just update_date has been update
    if created:
        async_post_save_created_handler.delay(instance)
    else:
        if len(instance.dirty_fields) > 1:
            async_post_save_handler.delay(instance)


def ad_search_post_save_handler(sender, instance, created, **kwargs):
    logger.info('Post save signal reached for AdSearch: %s' % (instance))
    # this should be optimize if search field is modified !
    # if it's only other conf file, we should'nt test for new/remove ads
    q = QueryDict(instance.search)
    filter = instance.content_type.model_class().filterset()(q or None)
    # here we remove ads that no more belongs to AdSearch
    ads = AdSearchResult.objects.filter(ad_search=instance)
    for ad in ads:
        logger.info("we work on %s to see if it always belong to ad_search" % ad.content_object)
        logger.info("Here is a list of all Ads contained in current AdSearch: %s" % filter.qs)
        if ad.content_object not in filter.qs:
            logger.info('We delete %s instance because it no more belongs to ad_search instance' % ad)
            ad.delete()
        else:
            logger.info("Ad: %s always in AdSearch %s" % (ad.content_object, instance))
    # here we save search AdSearchResult instances
    # so we add an Ad if it belongs to AdSearch
    for ad in filter.qs:
        ad_search_result, created = AdSearchResult.objects.get_or_create(
            ad_search=instance,
            content_type=instance.content_type,
            object_pk=ad.id)
        logger.info("We add an AdSearchResult with Ad: %s, it was created: %s" % (ad_search_result.content_object, created))
        # this below shoud help in case, ad_search change from not public to public
        # and we wan't to inform vendor that someone is interested in it ad
        #ad_search_result.save()


def ad_search_result_post_save_handler(sender, instance, created, **kwargs):
    logger.info('Post save signal reached for AdSearchResult: %s, containing Ad: %s' % (instance, instance.content_object))
    if created:
        geoad_new_relevant_ad_for_search.send(sender=Ad, ad=instance.content_object, relevant_search=instance)
        if instance.ad_search.public:
            geoad_new_interested_user.send(sender=Ad, ad=instance.content_object, interested_user=instance.ad_search.user)
