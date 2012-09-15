# coding=utf-8

from django.contrib.contenttypes.models import ContentType
from geoads.models import AdSearchResult, AdSearch
from django.http import QueryDict
from django.core.mail import send_mail


def updateadsearchresults(instance, status, search_filter):
    content_type = ContentType.objects.get_for_model(instance)
    if status == 1:
        # check for all ad_search that could be interested in that ad
        ad_searchs = AdSearch.objects.filter(
            content_type=content_type)

        # remove and ad when it no more belongs to an ad_search
        ad_searchs_having_ad = ad_searchs.filter(
            adsearchresult__object_pk=instance.pk)
        for ad_search in ad_searchs_having_ad:
            q = QueryDict(ad_search.search)
            filter = search_filter(q)
            if instance not in filter:
                # remove ad_result_search
                ad_search_result = AdSearchResult.get(
                    ad_search=ad_search, content_type=content_type,
                    object_pk=instance.pk)
                ad_search_result.delete()

        # add ad when it belongs to an ad_search
        # we could improve performance by removing ad_searchs_having_ad
        # from ad_searchs

        for ad_search in ad_searchs:
            q = QueryDict(ad_search.search)
            filter = search_filter(q)
            for ad in filter.qs:
                ad_search_result, created = AdSearchResult.objects.get_or_create(ad_search=ad_search,
                    content_type=ad_search.content_type, object_pk=ad.id)
                if created:
                    send_mail(u"Nouvelle annonce correspondant à votre recherche",
                        "%s" % (instance.get_absolute_url()), 'contact@achetersanscom.com',
                        [ad_search.user.email, ])
                    if ad_search.public:
                        # if ad_search i public, we inform the vendor that someone
                        # is interested by its add
                        send_mail(u"Un nouvel acheteur potentiel pour votre annonce",
                            "pour cette annonce : %s" % (instance.get_absolute_url()),
                            'contact@achetersanscom.com', [instance.user.email, ])
