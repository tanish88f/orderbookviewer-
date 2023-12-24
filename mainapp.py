from flask import Flask, jsonify, render_template
from flask_cors import CORS
import heapq
import requests
host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/futures/usdt/order_book'
query_param = 'contract=BTC_USDT'
r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)

response_json = r.json()

current = response_json.get('current')
id = response_json.get('id')
update = response_json.get('update')

asks = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
bids = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')]

order_book1 = {
    'asks': asks,
    'bids': bids
}
app = Flask(__name__,static_url_path='')
CORS(app)

class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []

    def add_limit_order(self, is_bid, price, quantity):
        order = Order(price, quantity)
        if is_bid:
            heapq.heappush(self.bids, (-price, order))
        else:
            heapq.heappush(self.asks, (price, order))

class Order:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

    def __eq__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.price == other.price and self.quantity == other.quantity

    def __lt__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.price < other.price

order_book = OrderBook()

# Add bids to the order book
for bid in order_book1['bids']:
    bid_price = float(bid[0])  # Access the price
    bid_quantity = bid[1]  # Access the quantity
    order_book.add_limit_order(True, bid_price, bid_quantity)

# Add asks to the order book
for ask in order_book1['asks']:
    ask_price = float(ask[0])  # Access the price
    ask_quantity = ask[1]  # Access the quantity
    order_book.add_limit_order(False, ask_price, ask_quantity)

"""from random import uniform
import numpy as np
"""
"""def add_random_orders(n):
    base_price = 100.0  # Set the base price
    desired_spread = 3.0  # Set the desired spread
    price_range = 30.0  # Set the range for price generation
    max_quantity = 1000  # Set the maximum quantity
    for _ in range(n):
        bid_price = round(base_price + uniform(0, price_range), 2)  # Generate a random bid price above the base price
        ask_price = round(base_price - uniform(0, price_range), 2)  # Generate a random ask price below the base price

        # Generate a quantity based on the price using a non-linear function
        bid_quantity = max(1, int(max_quantity * np.exp(-0.05 * (bid_price - base_price))))
        ask_quantity = max(1, int(max_quantity * np.exp(0.05 * (ask_price - base_price))))

        # Adjust the bid and ask prices if the spread is not within the desired range
        if bid_price - ask_price < desired_spread:
            bid_price = ask_price + desired_spread

        order_book.add_limit_order(True, bid_price, bid_quantity)  # Add the bid
        order_book.add_limit_order(False, ask_price, ask_quantity)  # Add the ask

add_random_orders(20)  # Add 40 random orders
"""

@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    bids = [(-price, order.quantity) for price, order in order_book.bids]
    asks = [(price, order.quantity) for price, order in order_book.asks]
    return jsonify({'bids': bids, 'asks': asks})

@app.route('/api/quote', methods=['GET'])
def get_quote():
    best_bid = -order_book.bids[0][0] if order_book.bids else None
    best_ask = order_book.asks[0][0] if order_book.asks else None
    return jsonify({'bid': best_bid, 'ask': best_ask})

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6005)