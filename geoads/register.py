from django.db.models.signals import post_save
from .events import ad_post_save_handler

def geoads_register(model_class):
    post_save.connect(ad_post_save_handler, sender=model_class,
                      dispatch_uid="ad_post_save_handler")
