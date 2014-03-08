from collections import defaultdict
from datetime import timedelta
from itertools import groupby
from operator import itemgetter
import logging
import uuid

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from blockchain_adapter import blockchain

from utils import get_protocol, get_authenticated_twitter_api

logger = logging.getLogger('bountyfulcoinsapp.models')


class Link(models.Model):
    url = models.URLField(unique=True)

    def __unicode__(self):
        return self.url


class Bounty(models.Model):
    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Bounties'

    link = models.ForeignKey(Link, verbose_name=_('Bounty URL'))
    title = models.CharField(_('Bounty Title'), max_length=200)
    user = models.ForeignKey(get_user_model())
    amount = models.DecimalField(_('Bounty Amount'), default=0.00,
                                 max_digits=20, decimal_places=2)
    currency = models.CharField(_('Bounty Currency'), default='BTC',
                                max_length=15)
    ctime = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return u'%s, %s' % (self.user.username, self.link.url)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('bounty_details', args=[str(self.id)])

    @property
    def full_url(self):
        return u"{protocol}{domain}{path}".format(
            protocol=get_protocol(getattr(self, '_request', None)),
            domain=Site.objects.get_current().domain.strip(' /'),
            path=self.get_absolute_url(),
        )

    def assign_tags_from_string(self, string):
        """
        Takes a list of string, by default sepererated by comma,
        and reassigns the tags to this bounty.
        """
        tag_names = string.split(',')
        self.tags.clear()  # remove existing tags before assigning new
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            self.tags.add(tag)

    @property
    def shared_date(self):
        try:
            return self.shared.last().date
        except SharedBounty.DoesNotExist:
            return None

    def share(self):
        """ Create a SharedBounty for this bounty """
        return SharedBounty.objects.get_or_create(bounty=self)

    def feature(self):
        """ Create a FeaturedBounty for this bounty """
        try:
            addr = Address.get_available_addresses().first()
        except Address.DoesNotExist:
            raise Exception('No assignable addresses found, '
                            'cannot feature bounty')
        self.featured = FeaturedBounty.objects.create(address=addr, bounty=self)
        return self.featured

    @property
    def is_featured(self):
        try:
            return bool(self.featured)
        except FeaturedBounty.DoesNotExist:
            return False

    def _get_tweet(self, request=None):
        self._request = request
        msg = (u"{b.ctime:%A} #bitcoin bounty paying {b.amount}"
               u" in {b.currency} {b.full_url} #bountyful").format(b=self)
        if hasattr(self, '_request'):
            delattr(self, '_request')
        return msg

    def send_tweet(self, request=None):
        logger.debug('Entering send_tweet')
        tweeter_status = self._get_tweet(request)
        api = get_authenticated_twitter_api()
        api.update_status(tweeter_status)


class Tag(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64, unique=True)
    bounties = models.ManyToManyField(Bounty, related_name='tags')

    def __unicode__(self):
        return self.name


class SharedBounty(models.Model):
    class Meta:
        ordering = ['-votes', '-date']
        verbose_name_plural = 'Shared bounties'

    bounty = models.ForeignKey(Bounty, unique=True, related_name='shared')
    date = models.DateTimeField(default=timezone.now)
    votes = models.IntegerField(default=1)
    users_voted = models.ManyToManyField(get_user_model())

    # if user decides to disable bounty later
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s, %s' % (self.bounty, self.votes)


class Address(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address_id = models.CharField(max_length=64, unique=True)

    verified_balance = models.DecimalField(default=0.00, max_digits=20,
                                           decimal_places=6)
    last_synced = models.DateTimeField(null=True, blank=True)

    @property
    def sync_required(self):
        if not settings.ADDRESSES_LIVE_SYNC:
            return False
        freq = timedelta(seconds=settings.ADDRESSES_SYNC_FREQUENCE)
        return (timezone.now() - self.last_synced) > freq

    def sync_verified_balance(self):
        """
        Using blockchain.info API get the latest balance of the Address.

        If a good result is returned, store it and update last_synced time.
        """
        res = blockchain.get_balance(self.address_id)
        if res is not None:
            self.verified_balance = res
            self.last_synced = timezone.now()
            self.save()
            return True
        return False

    @classmethod
    def get_available_addresses(cls):
        """
        Return assignable addresses, i.e: not related to a FeaturedBounty
        and have verified_balance of 0.00.
        """
        return cls.objects.filter(featured_bounty=None,
                                  verified_balance=0.00)

    @classmethod
    def bulk_create(cls, addr_list):
        """
        A helper method that inserts into the db the passed
        list of address dicts (excluding existing address ids).

        addr_list=[ {'name': 'abc', 'address_id': '1234'}, ... ]
        """
        # get and exclude dupes
        hashes = [a['address_id'] for a in addr_list]
        existing = cls.objects.filter(address_id__in=hashes).values_list(
            'address_id', flat=True)
        cls.objects.bulk_create([cls(**a) for a in addr_list
                                if a['address_id'] not in list(existing)])


class FeaturedBounty(models.Model):
    class Meta:
        ordering = ['-ctime']
        verbose_name_plural = 'Featured bounties'

    bounty = models.OneToOneField(Bounty, related_name='featured', null=True)
    address = models.OneToOneField(Address, unique=True,
                                   related_name='featured_bounty')
    ctime = models.DateTimeField(default=timezone.now)

    @property
    def enabled(self):
        if self.address.verified_balance >= settings.FEATURE_POST_MIN_CHARGE:
            return True
        elif self.address.last_synced is None or self.address.sync_required:
            res = self.address.sync_verified_balance()
            if res:  # balance was updated, check again
                return self.enabled
        # cannot verify payment was made, return False
        return False

    @classmethod
    def get_funded_entries(cls):
        return cls.objects.filter(
            address__verified_balance__gte=settings.FEATURE_POST_MIN_CHARGE)

    @property
    def target_address(self):
        """
        A wrapper property around the fwd address functionality falling
        back to using one of our available 0 addresses.
        """
        return self.get_forwarding_address() or self.address.address_id

    def get_forwarding_address(self):
        """
        If a receiving address is defined, return a fwd addr to it,
        otherwise return None
        """
        if settings.RECEIVING_ADDRESS is None:
            # we can now fallback to receiving into one of our addresses
            return None

        if not hasattr(self, '_fwd_addr'):  # memoize
            if self.payments.filter(amount=0).count() > 0:
                # if payment record with 0 amount exist, use latest fwd address
                last_zero_payment = self.payments.filter(amount=0).latest()
                if last_zero_payment.input_address:
                    self._fwd_addr = last_zero_payment.input_address
                    return self._fwd_addr

            # otherwise, generate a new address and relate to a payment record
            from django.core.urlresolvers import reverse
            callback_base = u"{protocol}{domain}{path}".format(
                protocol=get_protocol(getattr(self, '_request', None)),
                domain=Site.objects.get_current().domain.strip(' /'),
                path=reverse('callback')
            )
            pr = PaymentRecord(featured_bounty=self)
            pr.save()
            cb = '{base}?payment_id={id}&secret={uid}'.format(
                base=callback_base, id=pr.id, uid=pr.uid)
            addr = blockchain.get_forwarding_address(
                settings.RECEIVING_ADDRESS, cb)
            pr.input_address = addr
            pr.save()

            if not addr:
                logger.error('Could not get a forwarding address')
                # we can now fallback to receiving into one of our addresses
                return None
            self._fwd_addr = addr
        return self._fwd_addr

    def get_remaining_paid(self):
        """
        Return the sum of of the remaining amount total from all sums paid
        for this bounty featuring.
        """
        return sum(p.calculate_remaining
                   for p in self.payments.filter(verified=True))


def get_uuid():
    return uuid.uuid4().hex


class PaymentRecord(models.Model):
    class Meta:
        ordering = ['-ctime']
        get_latest_by = "ctime"

    featured_bounty = models.ForeignKey(FeaturedBounty, related_name='payments')
    uid = models.CharField(default=get_uuid, max_length=32)
    ctime = models.DateTimeField(default=timezone.now)
    mtime = models.DateTimeField(null=True)

    # post verification details
    verified_on = models.DateTimeField(null=True)
    amount = models.FloatField(default=0.0)
    verified = models.BooleanField(default=False)
    input_address = models.CharField(max_length=255, null=True)
    confirmatons = models.IntegerField(default=0)
    fwd_transaction = models.CharField(max_length=255, null=True)
    input_transaction = models.CharField(max_length=255, null=True)
    # remaining_amount = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        self.mtime = timezone.now()
        return super(PaymentRecord, self).save(*args, **kwargs)

    def calculate_remaining(self):
        """
        Get the remaning amount of this payment, meaning:
        original amount paid, reduced daily
        """
        delta_seconds = (timezone.now() - self.ctime).total_seconds()
        days_passed = int(delta_seconds / float(60 * 60 * 24))
        return self.amount - (days_passed * settings.FEATURE_POST_MIN_CHARGE)


def calculate_totals():
    bounties = sorted(
        list(SharedBounty.objects.values_list('bounty__currency',
                                              'bounty__amount')) +
        list(FeaturedBounty.get_funded_entries().values_list(
            'bounty__currency', 'bounty__amount')),
        key=itemgetter(0))
    totals = defaultdict(float)
    for currency, bounty_group in groupby(bounties, itemgetter(0)):
        totals[currency] += sum(float(b[1] or 0.0) for b in bounty_group)
    return dict(totals)
