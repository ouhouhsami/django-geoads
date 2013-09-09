#-*- coding: utf-8 -*-
from django.contrib.sites.models import Site

from .mails import (AdModifiedMessageEmail, AdModeratedMessageEmail,
                    BuyerToVendorMessageEmail, VendorToBuyerMessageEmail,
                    NewPotentialBuyerToVendorMessageEmail, NewAdToBuyerMessageEmail)

site = Site.objects.get_current()
default_context = {'site':site, 'site_name': site.name,
                   'site_url': 'http://%s' % (site.domain)}


def geoad_new_interested_user_callback(sender, ad, interested_user, mail_class=NewPotentialBuyerToVendorMessageEmail, **kwargs):
    context = dict(default_context, **{'to': ad.user.email, 'ad': ad, 'user': interested_user})
    msg = mail_class(context)
    msg.send([context['to'], ])


def geoad_new_relevant_ad_for_search_callback(sender, ad, relevant_search, mail_class=NewAdToBuyerMessageEmail, **kwargs):
    context = dict(default_context, **{'to': relevant_search.ad_search.user.email,
                                   'ad': ad, 'user':relevant_search.ad_search.user})
    msg = mail_class(context)
    msg.send([context['to'], ])


def geoad_user_message_callback(sender, ad, user, message, mail_class=BuyerToVendorMessageEmail, **kwargs):
    context = dict(default_context, **{'message': message, 'to': ad.user.email,
                                    'from': user.email, 'ad': ad, 'user': user})
    msg = mail_class(context)
    msg.send([context['to'], ])


def geoad_vendor_message_callback(sender, ad, ad_search, user, message, mail_class=VendorToBuyerMessageEmail, **kwargs):
    context = dict(default_context, **{'message': message, 'to': user.email, 'ad_search':ad_search,
                                    'from': ad.user.email, 'ad': ad, 'user': user})
    msg = mail_class(context)
    msg.send([context['to'], ])


def ad_post_save_callback(sender, ad, mail_class=AdModifiedMessageEmail, **kwargs):
    context = dict(default_context, **{'user': ad.user, 'to': ad.user.email, 'ad':ad})
    msg = mail_class(context)
    msg.send([context['to'], ])


def ad_post_moderation_callback(sender, instance, status, mail_class=AdModeratedMessageEmail, **kwargs):
    context = dict(default_context, **{'user': instance.user, 'to': instance.user.email,
                                    'ad':instance, 'status': status})
    msg = mail_class(context)
    msg.send([context['to'], ])

