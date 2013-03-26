#-*- coding: utf-8 -*-
from django.dispatch import Signal

geoad_new_interested_user = Signal(providing_args=['ad', 'interested_user'])
geoad_new_relevant_ad_for_search = Signal(providing_args=['ad', 'relevant_search'])
geoad_user_message = Signal(providing_args=['ad', 'user', 'message'])
geoad_vendor_message = Signal(providing_args=['ad', 'user', 'message'])
geoad_post_save_ended = Signal(providing_args=['ad'])
