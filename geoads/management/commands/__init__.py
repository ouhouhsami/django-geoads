from django.core.management.base import BaseCommand, CommandError
from geoads.models import AdSearch


class Command(BaseCommand):

    def handle(self, *args, **options):
        ad_searchs = AdSearch.objects.all()
        # launch search
        