#-*- coding: utf-8 -*-
import requests

from django.conf import settings
from django.contrib.gis.geos import Point


def geocode(address):
    if settings.GEOCODE == 'nominatim':
        params = {'q': address, 'format': 'json', 'addressdetails': '1', 'limit': '1', 'countrycodes': 'fr', 'polygon': '1'}
        r = requests.get("http://nominatim.openstreetmap.org/search", params=params)
        address = r.json[0]['address']
        location = Point(float(r.json[0]['lon']), float(r.json[0]['lat']), srid=900913)
        return {'address': address, 'location': location}
