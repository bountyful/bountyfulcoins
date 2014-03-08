from uuid import uuid4
import logging
import unittest

import requests

logging.basicConfig()
logger = logging.getLogger('blockchain_adapter')


URL_BASE = 'https://blockchain.info'
URL_BALANCE = '{base}/q/addressbalance/{addr}'
URL_FORWARD = ('{base}/api/receive')

CONFIRMATIONS_MIN = 6  # min recommended by blockchain docs


class BlockChainAdapter(object):
    """
    A simple wrapper around requests to query blockchain.info API.

    Currently supports getting a specified address balance
    """
    def __init__(self, *args, **kwargs):
        self.url_base = kwargs.get('URL_BASE', URL_BASE)
        self.url_balance = kwargs.get('URL_BALANCE', URL_BALANCE)
        self.url_fwd = kwargs.get('URL_FORWARD', URL_FORWARD)

    def get_balance_url(self, addr):
        return self.url_balance.format(base=self.url_base, addr=addr)

    def get_balance(self, address):
        logger.debug('Entering get_balance')

        res = requests.get(self.get_balance_url(address), params={
            'confirmations': CONFIRMATIONS_MIN})
        if not res.ok:
            logger.error('Could not get balance, server returned: %s - %s',
                         res.status_code, res.content)
            return None
        return float(res.content)

    def get_fwd_url(self):
        return self.url_fwd.format(base=self.url_base)

    def get_forwarding_address(self, address, callback_url):
        logger.debug('Entering get_balance')

        res = requests.get(self.get_fwd_url(), params={
            'method': 'create',
            'address': address,
            'callback': callback_url,
        })
        if not res.ok:
            logger.error('Could not get forwarding address, server returned: '
                         '%s - %s', res.status_code, res.content)
            return None
        response_dict = res.json()

        # parse response to verify it fwd addr is sending to the right place
        if response_dict.get('destination') != address:
            logger.error('Received destinatioon address %s is different than '
                         'the one requested (%s), aborting!',
                         response_dict.get('destination'), address)
            return None
        if response_dict.get('callback_url') != callback_url:
            logger.error('Received callback_url %s is different than the '
                         'one requested (%s), aborting!',
                         response_dict.get('callback_url'), callback_url)
            return None
        return unicode(response_dict.get('input_address'))

blockchain = BlockChainAdapter()


class TestBlockChainAdapter(unittest.TestCase):
    good_address = '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX'
    bad_address = 'NOT_REAL'

    def test_bad_address(self):
        res = blockchain.get_balance(self.bad_address)
        self.assertIsNone(res, "get_balance should have returned 'None'"
                          " for this address")

    def test_good_address(self):
        res = blockchain.get_balance(self.good_address)
        self.assertIsInstance(res, float, "get_balance should have returned"
                              " a float number fot this address")

    def test_getting_forwarding_address(self):
        cb = 'http://example.com/?some_id=1&secret=%s' % uuid4().hex
        res = blockchain.get_forwarding_address(self.good_address, cb)
        self.assertIsInstance(res, unicode,
                              "getting_forwarding_address should have returned"
                              " a unicode string")
        # self.assertEqual(first, second, msg)


if __name__ == '__main__':
    unittest.main()
