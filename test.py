import unittest
from flask_testing import TestCase
from index import app, OrderBook, Order

order_book = OrderBook()

class TestOrderBook(unittest.TestCase):
    def test_add_limit_order(self):
        order_book.add_limit_order(True, 100, 10)
        self.assertEqual(order_book.bids[0], (-100, Order(100, 10)))

class TestRoutes(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_orderbook_route(self):
        response = self.client.get('/api/orderbook')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'bids': [[100, 10]], 'asks': []})

    def test_quote_route(self):
        response = self.client.get('/api/quote')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'bid': 100, 'ask': None})

if __name__ == '__main__':
    unittest.main()