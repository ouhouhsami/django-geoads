#-*- coding: utf-8 -*-
import logging

from django.db import models
from django.contrib.gis.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


from autoslug import AutoSlugField
from jsonfield.fields import JSONField


from geoads.signals import geoad_new_interested_user


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


'''
class PublicAdSearchManager(models.Manager):
    """
    Ad Search Manager
    """
    #TODO fix for django1.5 needed get_query_set became get_queryset
    def get_query_set(self):
        return super(PublicAdSearchManager, self).get_query_set().filter(public=True)
'''


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
    public = models.BooleanField("Publier cette recherche ?", 
                                 help_text=u"Une recherche publique permet aux vendeurs ayant un bien correspondant à votre recherche de vous contacter.")
    description = models.TextField("Message aux vendeurs", null=True, blank=True, 
                                   help_text=u"Ce message est destiné aux vendeurs ayant un bien correspondant à votre recherche. Il sera publié avec votre annonce de recherche.")

    objects = models.Manager()
    #publics = PublicAdSearchManager()

    class Meta:
        db_table = 'ads_adsearch'

    def save(self, *args, **kwargs):
        previous_public = None
        if self.id is not None:
            previous_public = AdSearch.objects.get(id=self.id).public
        super(AdSearch, self).save(*args, **kwargs)  # Call the "real" save() method.
        if previous_public != self.public and self.public is True:
            # send mail to vendors
            ad_search_results = AdSearchResult.objects.filter(ad_search=self)
            for instance in ad_search_results:
                if instance.create_date < self.create_date or previous_public is False:
                    geoad_new_interested_user.send(sender=Ad, ad=instance.content_object, interested_user=self.user)


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
        # ensure that an ad is only present once for
        unique_together = ('ad_search', 'content_type', 'object_pk')


class AdManager(models.GeoManager):
    """
    Ad Manager
    anticipation of use for it
    no more used to get filterset linked to Ad model
    """
    #TODO fix for django1.5 needed get_query_set became get_queryset
    pass


class Ad(models.Model):
    """
    Ad abstract base model
    """
    user = models.ForeignKey(User)
    slug = AutoSlugField(populate_from='get_full_description',
                         always_update=True, unique=True)
    description = models.TextField("", null=True, blank=True)
    user_entered_address = models.CharField("Adresse", max_length=2550,
                                            help_text=u"Adresse complète, ex. : 5 rue de Verneuil Paris")
    address = JSONField(null=True, blank=True)
    location = models.PointField(srid=900913)
    pictures = generic.GenericRelation(AdPicture)
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    delete_date = models.DateTimeField(null=True, blank=True)

    ad_search_results = generic.GenericRelation(AdSearchResult,
                                                object_id_field="object_pk",
                                                content_type_field="content_type")

    objects = AdManager()

    default_filterset = 'geoads.filtersets.AdFilterSet'

    @classmethod
    def filterset(cls):
        """
        class method to get filterset for model
        TODO: raise configuration error if default_filterset not set on model
        """
        filterset_class = cls.default_filterset.split('.')[-1]
        module = ".".join(cls.default_filterset.split('.')[0:-1])
        mod = __import__(module, fromlist=[filterset_class])
        klass = getattr(mod, filterset_class)
        logger.info('%s' % klass)
        return klass
    
    def get_full_description(self, instance=None):
        raise NotImplementedError

    def _get_public_adsearch(self):
        #TODO should be just one queryset ! this is ugly
        ad_search_results_public = []
        for ad in self.ad_search_results.all():
            if ad.ad_search.public is True:
                ad_search_results_public.append(ad.ad_search)
        return ad_search_results_public

    public_adsearch = property(_get_public_adsearch)

    def __unicode__(self):
        return self.slug

    class Meta:
        abstract = True

# connect signals
from .receivers import *