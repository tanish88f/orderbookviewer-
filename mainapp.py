from flask import Flask, render_template, request
from flask_cors import CORS
import heapq
import requests
from flask_socketio import SocketIO
import time
import numpy as np

app = Flask(__name__, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")


host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/futures/usdt/order_book'
query_param = 'contract=BTC_USDT'
r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)

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



@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/update_symbol', methods=['POST'])
def update_symbol():
    data = request.get_json()
    symbol = data['symbol']
    global query_param
    query_param = f'contract={symbol}'
    return {'status': 'success'}

def fetch_order_book():
    while True:
        r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)
        response_json = r.json()
        asks = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')][:]  # Exclude the first ask
        bids = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
        order_book = {'asks': asks, 'bids': bids}  # Swap bids and asks here
        socketio.emit('orderbook', order_book)
        time.sleep(0.1)

def fetch_pricepaths():
    while True:
        r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)
        response_json = r.json()
        asks = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')][:]  # Exclude the first ask
        bids = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
        price_paths = monte()
        socketio.emit('price_paths', price_paths)
        time.sleep(0.1)

    
def generate_price_paths(mid_price_func, num_paths, num_steps, drift, volatility, time):
    dt = time / num_steps
    price_paths = []

    for _ in range(num_paths):
        price_path = [mid_price_func()]  # Initial mid-price
        for _ in range(num_steps):
            z = np.random.standard_normal()
            price = price_path[-1] * np.exp((drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * z)
            price_path.append(price)
        price_paths.append(price_path)
    
    return price_paths

def simple_mid_price():
    r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)
    response_json = r.json()
    asks = [[float(bid['p']), bid['s']] for bid in response_json.get('bids')][:]  # Exclude the first ask
    bids = [[float(ask['p']), ask['s']] for ask in response_json.get('asks')]
    mid_price = (asks[0][0] + bids[0][0]) / 2
    return mid_price

def monte():
    # Parameters for the simulation
    num_simulations = 10  # Number of simulated price paths
    num_time_steps = 100  # Number of time steps
    drift_value = 0.1  # Drift parameter for GBM
    volatility_value = 0.2  # Volatility parameter for GBM
    total_time = 1.0  # Total time horizon for simulation

    # Generate price paths using the chosen mid-price function
    price_paths = generate_price_paths(simple_mid_price, num_simulations, num_time_steps, drift_value, volatility_value, total_time)
    return price_paths

@socketio.on('symbol_change')
def handle_symbol_change(symbol):
    # Fetch new price paths for the new symbol
    new_price_paths = monte(symbol)

    # Emit a 'price_paths' event with the new price paths
    socketio.emit('price_paths', new_price_paths)


@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(fetch_order_book)
    socketio.start_background_task(fetch_pricepaths)
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6005)
