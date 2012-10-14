#-*- coding: utf-8 -*-

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.geos import Point
import requests

logger = logging.getLogger(__name__)


def ad_search_result_vendor_notification(ad):
    send_mail(u"Un nouvel acheteur potentiel pour votre annonce",
        "pour cette annonce : %s" % (ad.get_absolute_url()),
        'contact@achetersanscom.com', [ad.user.email, ])    # send mail
    logger.info("Send mail to vendor")


def geocode(address):
    if settings.GEOCODE == 'nominatim':
        params = {'q': address, 'format': 'json', 'addressdetails': '1', 'limit': '1', 'countrycodes': 'fr', 'polygon': '1'}
        r = requests.get("http://nominatim.openstreetmap.org/search", params=params)
        address = r.json[0]['address']
        location = Point(float(r.json[0]['lon']), float(r.json[0]['lat']), srid=900913)
        return {'address': address, 'location': location}
