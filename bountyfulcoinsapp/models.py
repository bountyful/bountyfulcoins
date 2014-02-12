from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Link(models.Model):
	url = models.URLField(unique=True)
	def __unicode__(self):
		return self.url

class bounty(models.Model):
	title = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	link = models.ForeignKey(Link)
	def __unicde__(self):
		return u'%s, %s' % (self.user.username, self.link.url)

class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True)
	bounties = models.ManyToManyField(bounty)
	def __unicode__(self):
		return self.name