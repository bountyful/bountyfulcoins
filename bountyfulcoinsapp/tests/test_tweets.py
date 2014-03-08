from django.core.urlresolvers import reverse

from django_webtest import WebTest
from mock import Mock

from ..models import Bounty
from .test_bounty import BountyCreateMixin
from .common import SiteDataMixin


class TestTweetBounty(BountyCreateMixin, SiteDataMixin, WebTest):
    fixtures = ['users', 'bounties', 'addresses']

    def test_full_url(self):
        # no request stored => default to http
        bounty = Bounty.objects.get(id=1)
        http_result = "http://example.com/bounty/1/details"
        https_result = "https://example.com/bounty/1/details"
        self.assertEqual(bounty.full_url, http_result)

        # http request stored on bounty
        bounty._request = Mock()
        bounty._request.is_secure = Mock(return_value=False)
        self.assertEqual(bounty.full_url, http_result)

        # https request stored on bounty
        bounty._request = Mock()
        bounty._request.is_secure = Mock(return_value=True)
        self.assertEqual(bounty.full_url, https_result)

    def test_tweet_msg_format(self):
        bounty = Bounty.objects.get(id=2)
        tweet_msg = bounty._get_tweet()
        weekday = bounty.ctime.strftime('%A')
        self.assertEqual(
            tweet_msg,
            "%s #bitcoin bounty paying 2000 in DOGE "
            "http://example.com/bounty/2/details #bountyful" % weekday)

    def test_tweeting_on_shared(self):
        data = self.good_data.copy()
        data['share'] = True
        bounty = self._create_bounty(data)
        Bounty.send_tweet.assert_called_once()
        self.assertTrue(bounty.shared.exists())

    def test_tweeting_on_featured(self):
        data = self.good_data.copy()
        data['featured'] = True
        bounty = self._create_bounty(data)
        Bounty.send_tweet.assert_called_once()
        self.assertTrue(bounty.is_featured)

    def test_dont_tweet_on_existing_save(self):
        """ Check that tweet is not sent upon change form save
        (but only upon creation - which is it's own test) """

        Bounty.send_tweet = Mock()
        bounty = Bounty.objects.get(id=2)
        self.assertTrue(bounty.is_featured)
        change_form = self._get_bounty_form(new=False, pk=bounty.pk)
        self.assertRedirects(change_form.submit(),
                             reverse('change_bounty', args=[bounty.pk]))
        Bounty.send_tweet.assert_not_called()
