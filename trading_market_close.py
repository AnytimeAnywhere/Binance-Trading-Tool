import json
import requests
from binance.client import Client
from binance.enums import *
import sys

# Declare vars
position = {}
position_each = {}

# symbol = sys.argv[1]  # The value passed as a command-line argument

# print( f"{symbol}")

# Specify the URL for the API endpoint that returns the API keys
api_config_url = 'http://49.12.154.55/real.json'
# api_config_url = 'http://49.12.154.34/APIs.json'

# Retrieve the API keys from the remote API endpoint
def trading_market_close(symbol):
    response = requests.get(api_config_url)
    global api_data
    api_data = json.loads(response.text)
    if not isinstance(api_data, dict):
        raise Exception("APIs file is not a valid JSON object")

    # Specify the symbol for which to retrieve open positions
    # symbol = input("Enter symbol to close position: ") # Prompt user to enter the symbol to close position

    for i in range( len(api_data['binance']) ):
        print( f"==> APIkey : {api_data['binance'][i]['api_key']}")
        try:
            # Connect to Binance API using the retrieved API keys
            client = Client(api_data['binance'][i]['api_key'], api_data['binance'][i]['api_secret'], testnet=api_data['binance'][i]['testnet'])
            # Retrieve open positions for the specified symbol
            positions = client.futures_position_information(symbol=symbol)
        except Exception as e:
            print(f"    !!!! An exception occurred: {e}\n")
            continue
        # Loop through the positions and print the direction and size of each position
        for pos in positions:
            if float(pos['positionAmt']) > 0:
                print(f"{symbol} long position: {pos['positionAmt']}")
                # Close long position at market price
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity=pos['positionAmt']
                )
                print(order)
            elif float(pos['positionAmt']) < 0:
                print(f"{symbol} short position: {-float(pos['positionAmt'])}")
                # Close short position at market price
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity = abs(float(pos['positionAmt'])) # Use abs() to get the absolute value of positionAmt
                )
                print(order)
            print( "\n")


