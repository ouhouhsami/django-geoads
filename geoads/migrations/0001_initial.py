# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AdPicture'
        db.create_table('ads_adpicture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('image', self.gf('stdimage.fields.StdImageField')(max_length=100, thumbnail_size={'width': 100, 'force': None, 'height': 100}, size={'width': 640, 'force': None, 'height': 500})),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('ads', ['AdPicture'])

        # Adding model 'AdContact'
        db.create_table('ads_adcontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.UserProfile'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ads', ['AdContact'])

        # Adding model 'AdSearch'
        db.create_table('ads_adsearch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('search', self.gf('django.db.models.fields.CharField')(max_length=2550)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.UserProfile'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('ads', ['AdSearch'])

        # Adding model 'HomeForSaleAd'
        db.create_table('ads_homeforsalead', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.UserProfile'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('address', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=900913)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('habitation_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('surface', self.gf('django.db.models.fields.IntegerField')()),
            ('surface_carrez', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('nb_of_rooms', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('nb_of_bedrooms', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('energy_consumption', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('emission_of_greenhouse_gases', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('ground_surface', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('floor', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('ground_floor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('top_floor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('not_overlooked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('elevator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('intercom', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('digicode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('doorman', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('heating', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('kitchen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('duplex', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('swimming_pool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alarm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('air_conditioning', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fireplace', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('terrace', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('balcony', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('separate_dining_room', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('separate_toilet', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bathroom', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('shower', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('separate_entrance', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cellar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parking', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('orientation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None, db_index=True)),
        ))
        db.send_create_signal('ads', ['HomeForSaleAd'])

        # Adding model 'HomeForRentAd'
        db.create_table('ads_homeforrentad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.UserProfile'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('address', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=900913)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('habitation_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('surface', self.gf('django.db.models.fields.IntegerField')()),
            ('surface_carrez', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('nb_of_rooms', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('nb_of_bedrooms', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('energy_consumption', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('emission_of_greenhouse_gases', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('ground_surface', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('floor', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('ground_floor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('top_floor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('not_overlooked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('elevator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('intercom', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('digicode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('doorman', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('heating', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('kitchen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('duplex', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('swimming_pool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alarm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('air_conditioning', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fireplace', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('terrace', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('balcony', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('separate_dining_room', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('separate_toilet', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bathroom', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('shower', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('separate_entrance', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cellar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parking', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('orientation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('colocation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('furnished', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ads', ['HomeForRentAd'])


    def backwards(self, orm):
        
        # Deleting model 'AdPicture'
        db.delete_table('ads_adpicture')

        # Deleting model 'AdContact'
        db.delete_table('ads_adcontact')

        # Deleting model 'AdSearch'
        db.delete_table('ads_adsearch')

        # Deleting model 'HomeForSaleAd'
        db.delete_table('ads_homeforsalead')

        # Deleting model 'HomeForRentAd'
        db.delete_table('ads_homeforrentad')


    models = {
        'ads.adcontact': {
            'Meta': {'object_name': 'AdContact'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.UserProfile']"})
        },
        'ads.adpicture': {
            'Meta': {'object_name': 'AdPicture'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'thumbnail_size': "{'width': 100, 'force': None, 'height': 100}", 'size': "{'width': 640, 'force': None, 'height': 500}"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'ads.adsearch': {
            'Meta': {'object_name': 'AdSearch'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'search': ('django.db.models.fields.CharField', [], {'max_length': '2550'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.UserProfile']"})
        },
        'ads.homeforrentad': {
            'Meta': {'object_name': 'HomeForRentAd'},
            'address': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alarm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'balcony': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bathroom': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cellar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'colocation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'digicode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doorman': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duplex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'elevator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'emission_of_greenhouse_gases': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'energy_consumption': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'fireplace': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'furnished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ground_floor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ground_surface': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'habitation_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'heating': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intercom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kitchen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913'}),
            'nb_of_bedrooms': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'nb_of_rooms': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'not_overlooked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'orientation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parking': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'separate_dining_room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'separate_entrance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'separate_toilet': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shower': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'surface': ('django.db.models.fields.IntegerField', [], {}),
            'surface_carrez': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'swimming_pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terrace': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'top_floor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.UserProfile']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ads.homeforsalead': {
            'Meta': {'object_name': 'HomeForSaleAd'},
            'address': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alarm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'balcony': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bathroom': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cellar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'digicode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doorman': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duplex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'elevator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'emission_of_greenhouse_gases': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'energy_consumption': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'fireplace': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ground_floor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ground_surface': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'habitation_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'heating': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intercom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kitchen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913'}),
            'nb_of_bedrooms': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'nb_of_rooms': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'not_overlooked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'orientation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parking': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'separate_dining_room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'separate_entrance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'separate_toilet': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shower': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'surface': ('django.db.models.fields.IntegerField', [], {}),
            'surface_carrez': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'swimming_pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terrace': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'top_floor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.UserProfile']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'profiles.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'email_alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['ads']
