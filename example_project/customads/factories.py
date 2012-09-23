
import random
import factory
from pygeocoder import Geocoder

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.auth.hashers import make_password

from models import TestAd


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

    '''
    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user
    '''

class TestAdFactory(factory.Factory):
    FACTORY_FOR = TestAd

    brand = factory.Sequence(lambda n: 'brand%s' % n)
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
        #kwargs.pop('location', None)
        test_ad = super(TestAdFactory, cls)._prepare(create, location=location, **kwargs)
        return test_ad
