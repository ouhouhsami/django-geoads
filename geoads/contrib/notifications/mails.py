#-*- coding: utf-8 -*-
from mail_factory import factory
from mail_factory.mails import BaseMail


class AdModifiedMessageEmail(BaseMail):
    """
    Ad Modified Message mail
    Used when a user update a new ad
    """
    template_name = 'ad_modified_email'
    params = ['user', 'site_name', 'site_url']

factory.register(AdModifiedMessageEmail)


class AdModeratedMessageEmail(BaseMail):
    """
    Override the default mail sent from moderation
    """
    template_name = 'ad_moderated_email'
    params = ['user', 'site_name', 'site_url']


class UserSignIn(BaseMail):
    """
    User Sign In
    """
    template_name = 'user_sign_in'
    params = ['user', 'site_name', 'site_url']

factory.register(UserSignIn)


class BuyerToVendorMessageEmail(BaseMail):
    """
    User message email from buyer to vendor for an Ad
    """
    template_name = 'to_vendor_message'
    params = ['user', 'site_name', 'site_url']

factory.register(BuyerToVendorMessageEmail)


class VendorToBuyerMessageEmail(BaseMail):
    """
    User message email from vendor to buyer for an Ad
    """
    template_name = 'to_buyer_message'
    params = ['user', 'site_name', 'site_url', 'message', 'ad', 'ad_search', 'from']

factory.register(VendorToBuyerMessageEmail)


class NewPotentialBuyerToVendorMessageEmail(BaseMail):
    """
    Mail sent to vendor when a user has it search coincides with it ad
    """
    template_name = 'to_vendor_potential_buyer'
    params = ['user', 'site_name', 'site_url']

factory.register(NewPotentialBuyerToVendorMessageEmail)


class NewAdToBuyerMessageEmail(BaseMail):
    """
    Mail sent to inform a user that a new ad corresponds to it search
    """
    template_name = 'to_buyer_potential_ad'
    params = ['user', 'site_name', 'site_url']

factory.register(NewAdToBuyerMessageEmail)
