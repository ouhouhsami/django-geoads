import random
import factory
from pygeocoder import Geocoder

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

from geoads.models import Ad, AdSearch

from models import TestAd, TestBooleanAd


ADDRESSES = ["13 Place d'Aligre, Paris",
    "22 rue Esquirol, Paris",
    "1 Avenue des Aqueducs, Arcueil",
    "1 place du Chatelet, Paris", ]


class UserFactory(factory.Factory):
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


class BaseAdFactory(factory.Factory):
    FACTORY_FOR = Ad

    user_entered_address = random.choice(ADDRESSES)
    user = factory.SubFactory(UserFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        user_entered_address = kwargs['user_entered_address']
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


class TestBooleanAdFactory(BaseAdFactory):
    FACTORY_FOR = TestBooleanAd

    boolean = random.choice([True, False])


class TestAdSearchFactory(factory.Factory):
    FACTORY_FOR = AdSearch

    user = factory.SubFactory(UserFactory)
    #content_type = ContentType.objects.get_for_model(TestAd) it seems that testad not created ! TODO: resolve this for testing purpose
