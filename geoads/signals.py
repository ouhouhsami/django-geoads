# coding=utf-8
import logging

from geoads.models import AdSearchResult, AdSearch
from django.http import QueryDict
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType


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
    '''
    Utils function that return True if an Ad belongs to an AdSearch
    '''
    q = QueryDict(ad_search.search)
    filter = ad_search.content_type.model_class().filterset(q or None)
    # here we test if current_ad is in results of filter
    if current_ad in filter.qs:
        return True
    else:
        return False


def ad_post_save_handler(sender, instance, **kwargs):
    # we must test and do 2 things
    #print 'POST SAVE AD HANDLER'
    # remove the ad to adsearch it does not more belongs to
    q = AdSearch.objects.filter(adsearchresult__object_pk=instance.pk,
        adsearchresult__content_type=ContentType.objects.get_for_model(instance))
    for ad_search in q:
        if not _is_ad_in_ad_search(instance, ad_search):
            # remove add
            AdSearchResult.objects.get(ad_search=ad_search, object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance)).delete()

    # add the ad to adsearch it belongs to
    q = AdSearch.objects.exclude(adsearchresult__object_pk=instance.pk,
        adsearchresult__content_type=ContentType.objects.get_for_model(instance))
    for ad_search in q:
        if _is_ad_in_ad_search(instance, ad_search):
            AdSearchResult(ad_search=ad_search, object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance)).save()


def ad_search_post_save_handler(sender, instance, created, **kwargs):
    logger.info('Ad search instance %s was saved' % (instance))
    #print 'POST SAVE AD SEARCH HANDLER'
    if created:
        logger.info('It\'s a new instance')
    else:
        logger.info('not a new instance')
    q = QueryDict(instance.search)
    filter = instance.content_type.model_class().filterset(q or None)
    # here we remove ads that no more belongs to AdSearch
    ads = AdSearchResult.objects.filter(ad_search=instance)
    for ad in ads:
        if ad not in filter.qs:
            ad.delete()
    # here we save search AdSearchResult instances
    # so we add an Ad if it belongs to AdSearch
    for ad in filter.qs:
        ad_search_result, created = AdSearchResult.objects.get_or_create(
            ad_search=instance,
            content_type=instance.content_type,
            object_pk=ad.id)


def ad_search_result_post_save_handler(sender, instance, created, **kwargs):
    #print 'POST SAVE AD SEARCH RESULT HANDLER'
    if created:
        send_mail(u"Nouvelle annonce correspondant à votre recherche",
            "%s" % (instance.content_object.get_absolute_url()), 'contact@achetersanscom.com',
            [instance.ad_search.user.email, ])
        if instance.ad_search.public:
            # if ad_search i public, we inform the vendor that someone
            # is interested by its add
            send_mail(u"Un nouvel acheteur potentiel pour votre annonce",
                "pour cette annonce : %s" % (instance.content_object.get_absolute_url()),
                'contact@achetersanscom.com', [instance.content_object.user.email, ])    # send mail
