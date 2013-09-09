import random
import factory
from pygeocoder import Geocoder

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.conf import settings

from geoads.models import Ad, AdSearch

from .models import TestAd, TestNumberAd, TestModeratedAd


ADDRESSES = ["13 Place d'Aligre, Paris",
    "22 rue Esquirol, Paris",
    "1 Avenue des Aqueducs, Arcueil",
    "1 place du Chatelet, Paris", ]


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: "user %s" % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)

    @classmethod
    def _prepare(cls, create, password=None, **kwargs):
        return super(UserFactory, cls)._prepare(
            create,
            password=make_password(password),
            **kwargs
        )


class BaseAdFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Ad

    user_entered_address = random.choice(ADDRESSES)
    user = factory.SubFactory(UserFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        user_entered_address = kwargs['user_entered_address']
        if settings.BYPASS_GEOCODE == True:
            location = 'POINT (2.3303780000000001 48.8683559999999986)'
        else:
            try:
                geocode = Geocoder.geocode(user_entered_address.encode('ascii', 'ignore'))
                coordinates = geocode[0].coordinates
                location = str(Point(coordinates[1], coordinates[0], srid=900913))
            except:
                location = 'POINT (2.3316097000000000 48.8002050999999994)'
        test_ad = super(BaseAdFactory, cls)._prepare(create, location=location, **kwargs)
        return test_ad


class TestAdFactory(BaseAdFactory):
    FACTORY_FOR = TestAd

    brand = factory.Sequence(lambda n: 'brand%s' % n)


class TestNumberAdFactory(BaseAdFactory):
    FACTORY_FOR = TestNumberAd

    number = factory.Iterator([1, 2, None, 3, 4, None])


class TestModeratedAdFactory(BaseAdFactory):
    FACTORY_FOR = TestModeratedAd

    brand = factory.Sequence(lambda n: 'brand%s' % n)


class TestAdSearchFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = AdSearch

    user = factory.SubFactory(UserFactory)
    #content_type = ContentType.objects.get_for_model(TestAd) it seems that testad not created ! TODO: resolve this for testing purpose
