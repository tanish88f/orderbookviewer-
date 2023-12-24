from flask import Flask, jsonify, render_template
from flask_cors import CORS
import heapq
import requests
from flask_socketio import SocketIO, emit
import time
app = Flask(__name__, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")


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

asks  = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
bids = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')]

order_book1 = {
    'asks': asks,
    'bids': bids
}

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

def emit_orderbook():
    bids = [(-price, order.quantity) for price, order in order_book.bids]
    asks = [(price, order.quantity) for price, order in order_book.asks]
    socketio.emit('orderbook', {'bids': bids, 'asks': asks})

@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    emit_orderbook()
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

def fetch_order_book():
    while True:
        r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)
        response_json = r.json()
        asks = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')][:]  # Exclude the first ask
        bids = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
        order_book = {'asks': asks, 'bids': bids}  # Swap bids and asks here
        socketio.emit('orderbook', order_book)
        time.sleep(0.2)

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(fetch_order_book)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6005)
