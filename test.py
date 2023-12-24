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

order_book = {
    'asks': asks,
    'bids': bids
}
print(order_book)