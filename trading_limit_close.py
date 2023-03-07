#Base import
import json
import os
import sys
import requests
from datetime import datetime
import time 
from time import sleep, strftime
#Binance import
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

# Declare vars
orders = {}
orders_each = {}
configs = {}

#api_config_url
api_config_url = 'http://49.12.154.55/real.json'
# api_config_url = 'http://49.12.154.34/APIs.json'
# http://49.12.154.55/real.json
def traing_limit_close(symbol):
    try: 
        response = requests.get(api_config_url)
        global api_data
        api_data = json.loads(response.text)
        if not isinstance(api_data, dict):
            raise Exception("APIs file is not a valid JSON object")
        for i in range( len(api_data['binance']) ):
            try:
                client = Client(api_data['binance'][i]['api_key'], api_data['binance'][i]['api_secret'], testnet=api_data['binance'][i]['testnet'])
                try:
                    # Get all open orders for the symbol
                    orders = client.futures_get_open_orders(symbol=symbol)

                    # Cancel all open orders for the symbol
                    for order in orders:
                        result = client.futures_cancel_order(symbol=symbol, orderId=order['orderId'])
                        print(f"Cancelled order {order['orderId']}")

                    print(f"All open orders for {symbol} of {api_data['binance'][i]['api_key']} have been cancelled.")
                except Exception as e:
                    print(f"Error cancelling orders: {e}")

            except Exception as e:
                print(f"Error cancelling orders for API key {i+1}: {e}")
    except Exception as e:
        print(f"\nLine : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}")
def loadConfig():
    try:
        with open('config.json') as f:
            global configs
            configs = json.load(f)
            print(configs)
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise e
# if __name__ == "__main__":
#     symbol = sys.argv[1]  # The value passed as a command-line argument
#     main()