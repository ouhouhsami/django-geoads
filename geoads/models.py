# coding=utf-8
import logging

from django.db import models
from django.contrib.gis.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import QueryDict

from autoslug import AutoSlugField
from jsonfield.fields import JSONField

logger = logging.getLogger(__name__)


class AdPicture(models.Model):
    """
    Ad picture model

    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to="pictures")
    title = models.CharField('Description de la photo', max_length=255,
                             null=True, blank=True)

    class Meta:
        db_table = 'ads_adpicture'


class AdContact(models.Model):
    """
    Ad contact model

    """
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_pk")
    message = models.TextField('Votre message')

    class Meta:
        db_table = 'ads_adcontact'


class AdSearch(models.Model):
    """
    AdSearch base

    Application using this need to have a proxy model
    to define unicode string representation of each
    AdSearch depending on ad fields.
    """
    search = models.CharField(max_length=2550)
    user = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    public = models.BooleanField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'ads_adsearch'


class AdSearchResult(models.Model):
    """
    Ad search result

    Hold ad which corresponds to an AdSearch instance
    """
    ad_search = models.ForeignKey(AdSearch)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_pk")
    create_date = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField()

    class Meta:
        db_table = 'ads_adsearchresult'


class Ad(models.Model):
    """
    Ad abstract base model

    """
    user = models.ForeignKey(User)
    slug = AutoSlugField(populate_from='get_full_description',
                         always_update=True, unique=True)
    description = models.TextField("", null=True, blank=True)
    user_entered_address = models.CharField("Adresse", max_length=2550,
            help_text="Adresse complète, ex. : <i>5 rue de Verneuil Paris</i>")
    address = JSONField(null=True, blank=True)
    location = models.PointField(srid=900913)
    pictures = generic.GenericRelation(AdPicture)
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    delete_date = models.DateTimeField(null=True, blank=True)
    visible = models.BooleanField()  # this shoud go to children class w/ moderation feature

    ad_search_results = generic.GenericRelation(AdSearchResult,
        object_id_field="object_pk", content_type_field="content_type")

    objects = models.GeoManager()

    filterset = None  # static var that hold the related filterset

    def get_full_description(self, instance=None):
        """return a resume description for slug"""
        return self.slug

    def __unicode__(self):
        return self.slug

    class Meta:
        abstract = True


@receiver(post_save, sender=AdSearch)
def ad_search_post_save_handler(sender, instance, created, **kwargs):
    logger.info('Ad search instance %s was saved' % (instance))
    if created:
        logger.info('It\'s a new instance')
    else:
        logger.info('not a new instance')
    q = QueryDict(instance.search)
    filter = instance.content_type.model_class().filterset(q or None)
    # here we save search AdSearchResult instances
    for ad in filter.qs:
        ad_search_result, created = AdSearchResult.objects.get_or_create(
            ad_search=instance,
            content_type=instance.content_type,
            object_pk=ad.id)
