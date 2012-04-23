import django_filters
from geoads.models import Ad

class AdFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        # improve : set default to none if key doesnt exist
        try:
            search = kwargs['search']
            del kwargs['search']
        except:
            search = None
        super(AdFilterSet, self).__init__(*args, **kwargs)
    class Meta:
        model = Ad