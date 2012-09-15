from django.core.management.base import BaseCommand, CommandError
from geoads.models import AdSearch
from django.http import QueryDict
from geoads.models import AdSearchResult

try:
    from sites.achetersanscom.ads.filtersets import HomeForSaleAdFilterSet
except ImportError:
    pass


class Command(BaseCommand):
    def handle(self, *args, **options):
        ad_searchs = AdSearch.objects.all()
        for ad_search in ad_searchs:
            # content_type
            if ad_search.content_type.model == 'homeforsalead':
                q = QueryDict(ad_search.search)
                filter = HomeForSaleAdFilterSet(q)
                for ad in filter.qs:
                    ad_search_result, created = AdSearchResult.objects.get_or_create(ad_search=ad_search,
                        content_type=ad_search.content_type, object_pk=ad.id)
                    print created
