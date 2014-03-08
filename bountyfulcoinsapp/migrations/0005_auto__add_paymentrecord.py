# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PaymentRecord'
        db.create_table(u'bountyfulcoinsapp_paymentrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('featured_bounty', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['bountyfulcoinsapp.FeaturedBounty'])),
            ('uid', self.gf('django.db.models.fields.CharField')(default='48e3f4b3cb2141869c8feba063906801', max_length=32)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('verified_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('input_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('confirmatons', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fwd_transaction', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('input_transaction', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'bountyfulcoinsapp', ['PaymentRecord'])


    def backwards(self, orm):
        # Deleting model 'PaymentRecord'
        db.delete_table(u'bountyfulcoinsapp_paymentrecord')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bountyfulcoinsapp.address': {
            'Meta': {'object_name': 'Address'},
            'address_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'verified_balance': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '6'})
        },
        u'bountyfulcoinsapp.bounty': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Bounty'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'BTC'", 'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bountyfulcoinsapp.Link']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'bountyfulcoinsapp.featuredbounty': {
            'Meta': {'ordering': "['-ctime']", 'object_name': 'FeaturedBounty'},
            'address': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'featured_bounty'", 'unique': 'True', 'to': u"orm['bountyfulcoinsapp.Address']"}),
            'bounty': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'featured'", 'unique': 'True', 'null': 'True', 'to': u"orm['bountyfulcoinsapp.Bounty']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'bountyfulcoinsapp.link': {
            'Meta': {'object_name': 'Link'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'bountyfulcoinsapp.paymentrecord': {
            'Meta': {'ordering': "['-ctime']", 'object_name': 'PaymentRecord'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'confirmatons': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'featured_bounty': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['bountyfulcoinsapp.FeaturedBounty']"}),
            'fwd_transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'input_transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'48d2ea1d0b1b4ea798d6a0877e437e87'", 'max_length': '32'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verified_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'bountyfulcoinsapp.sharedbounty': {
            'Meta': {'ordering': "['-votes', '-date']", 'object_name': 'SharedBounty'},
            'bounty': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared'", 'unique': 'True', 'to': u"orm['bountyfulcoinsapp.Bounty']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users_voted': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'bountyfulcoinsapp.tag': {
            'Meta': {'ordering': "['name']", 'object_name': 'Tag'},
            'bounties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': u"orm['bountyfulcoinsapp.Bounty']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bountyfulcoinsapp']