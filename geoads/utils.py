# coding=utf-8
import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def ad_search_result_vendor_notification(ad):
    send_mail(u"Un nouvel acheteur potentiel pour votre annonce",
        "pour cette annonce : %s" % (ad.get_absolute_url()),
        'contact@achetersanscom.com', [ad.user.email, ])    # send mail
    logger.info("Send mail to vendor")
