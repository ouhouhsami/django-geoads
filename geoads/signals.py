#-*- coding: utf-8 -*-
import logging

from geoads.models import AdSearchResult, AdSearch
from django.http import QueryDict
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType

from utils import ad_search_result_vendor_notification


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


def _is_ad_in_ad_search(current_ad, ad_search):
    """
    Utils function that returns True if an Ad belongs to an AdSearch

    """
    q = QueryDict(ad_search.search)
    #logger.info('QueryDict for filtering Ads that could belong to: %s' % q)
    #logger.info('\t\t_is_ad_in_ad_search Ad Search content_type: %s' % ad_search.content_type)
    #logger.info('\t\t_is_ad_in_ad_search Filterset used: %s' % ad_search.content_type.model_class().filterset)
    filter = ad_search.content_type.model_class().filterset(q or None)
    # here we test if current_ad is in results of filter
    if current_ad in filter.qs:
        logger.info('\t\t %s in %s' % (current_ad, ad_search))
        return True
    else:
        logger.info('\t\t %s not in %s' % (current_ad, ad_search))
        return False


def ad_post_save_handler(sender, instance, **kwargs):
    # we must test and do 2 things
    logger.info('Post save signal reached for Ad: %s' % (instance))
    # remove the ad to adsearch it does not more belongs to
    q = AdSearch.objects.filter(adsearchresult__object_pk=instance.pk,
        adsearchresult__content_type=ContentType.objects.get_for_model(instance))
    logger.info('We remove the ad to adsearchs it does not more belongs to')
    if q.count() == 0:
        logger.info('\tFor the moment, our Ad:%s doesn\'t belong to any of our AdSearch' % (instance))
    for ad_search in q:
        logger.info('\tTest on AdSearch:%s' % (ad_search))
        if not _is_ad_in_ad_search(instance, ad_search):
            # remove add
            logger.info('Ad: %s was allready inside an AdSearch: %s, but now we remove it' % (instance, ad_search))
            AdSearchResult.objects.get(ad_search=ad_search, object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance)).delete()
        else:
            logger.info('Ad: %s was allready inside an AdSearch: %s, and we keep it' % (instance, ad_search))
    # add the ad to adsearch it belongs to
    logger.info('We add the ad to adsearch it belongs to')
    q = AdSearch.objects.exclude(adsearchresult__object_pk=instance.pk,
        adsearchresult__content_type=ContentType.objects.get_for_model(instance))
    for ad_search in q:
        logger.info('\tTest on AdSearch:%s' % (ad_search))
        if _is_ad_in_ad_search(instance, ad_search):
            logger.info('Ad: %s wasn\'t allready inside an AdSearch: %s, now we add it' % (instance, ad_search))
            AdSearchResult(ad_search=ad_search, object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance)).save()
        else:
            logger.info('Ad: %s wasn\'t allready inside an AdSearch: %s, and doesn\'t belong to it' % (instance, ad_search))


def ad_search_post_save_handler(sender, instance, created, **kwargs):
    logger.info('Post save signal reached for AdSearch: %s' % (instance))
    # this should be optimize if search field is modified !
    # if it's only other conf file, we should'nt test for new/remove ads
    if created:
        logger.info('New instance of AdSearch')
    else:
        logger.info('Not a new instance of Adsearch')
    q = QueryDict(instance.search)
    filter = instance.content_type.model_class().filterset(q or None)
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
        send_mail(u"Nouvelle annonce correspondant à votre recherche",
            "%s" % (instance.content_object.get_absolute_url()), 'contact@achetersanscom.com',
            [instance.ad_search.user.email, ])
        logger.info("Send mail to %s for %s: it is inside it adsearch !" % (instance.ad_search.user.email, instance.content_object))
        #print instance.content_object.get_absolute_url()
        if instance.ad_search.public:
            #if instance.create_date < instance.ad_search.create_date:
            # if ad_search is public, we inform the vendor that someone
            # is interested by its add
            ad_search_result_vendor_notification(instance.content_object)
            #send_mail(u"Un nouvel acheteur potentiel pour votre annonce",
            #    "pour cette annonce : %s" % (instance.content_object.get_absolute_url()),
            #    'contact@achetersanscom.com', [instance.content_object.user.email, ])    # send mail
