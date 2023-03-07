#Base import
import json
import os
import requests
from datetime import datetime
from time import sleep, strftime

#Binance import
from binance.client import Client
from binance.enums import *
from binance.helpers import round_step_size

# Declare vars
orders = {}
orders_each = {}
configs = {}

#creating orders folder
cwd = os.getcwd()
os.makedirs(os.path.join(cwd, 'orders'), exist_ok=True)

#api_config_url
api_config_url = 'http://49.12.154.55/real.json'
# api_config_url = 'http://49.12.154.34/APIs.json'

#get tick size
def get_tick_size(info, symbol):
    for symbol_info in info['symbols']:
        if symbol_info['symbol'] == symbol:
            for symbol_filter in symbol_info['filters']:
                if symbol_filter['filterType'] == 'PRICE_FILTER':
                    return float(symbol_filter['tickSize'])

#get step size
def get_step_size(info, symbol):
    for symbol_info in info['symbols']:
        if symbol_info['symbol'] == symbol:
            for symbol_filter in symbol_info['filters']:
                if symbol_filter['filterType'] == 'LOT_SIZE':
                    return float(symbol_filter['stepSize'])
                

def setOdersList():
    try: 
        loadConfig() 
        response = requests.get(api_config_url)
        global api_data
        api_data = json.loads(response.text)
        if not isinstance(api_data, dict):
            raise Exception("APIs file is not a valid JSON object")
        orders_each = {}
        orders_each['binance'] = {}
        for i in range( len(api_data['binance']) ):
            orders_each['binance']['api_key'] = api_data['binance'][i]['api_key']
            orders_each['binance']['api_secret'] = api_data['binance'][i]['api_secret']
            orders_each['binance']['testnet'] = api_data['binance'][i]['testnet']

            print(f"\n==> {api_data['binance'][i]['api_key']}\n")

            orders_each['trading_params'] = configs['trading_params']
            try:
                client = Client(api_data['binance'][i]['api_key'], api_data['binance'][i]['api_secret'], testnet=api_data['binance'][i]['testnet'])
                
                symbol = orders_each['trading_params']['symbol']
                leverage = int(orders_each['trading_params']['leverage'])
                order_quantity_pct = float(orders_each['trading_params']['order_quantity_pct'])
                take_profit_price = float(orders_each['trading_params']['take_profit_price'])
                stop_loss_price = float(orders_each['trading_params']['stop_loss_price'])
                limit_price = float(orders_each['trading_params']['limit_price'])


                client.futures_change_leverage(symbol=symbol, leverage=int(leverage))
                print(f"Changed leverage to {leverage}x for {api_data['binance'][i]['api_key']}")
            except Exception as e:
                print(f"    !!!   {api_data['binance'][i]['api_key']} is fuck")
                continue

            account = client.futures_account()
            for balance in account['assets']:
                if balance['asset'] == 'USDT':
                    available_balance = float(balance['availableBalance'])

            amount = available_balance * int(leverage) * (float(order_quantity_pct) / 100) / float(limit_price)

            info = client.futures_exchange_info()

            amount = round_step_size(amount, get_step_size(info, symbol))

            price = round_step_size(float(limit_price), get_tick_size(info, symbol))
            take_profit = round_step_size(float(take_profit_price), get_tick_size(info, symbol))
            stop_loss = round_step_size(float(stop_loss_price), get_tick_size(info, symbol))

            symbol_price = client.get_symbol_ticker(symbol=symbol)['price']

            if take_profit > stop_loss:
                main_order = SIDE_BUY
                tp_sl_order = SIDE_SELL
            else:
                main_order = SIDE_SELL
                tp_sl_order = SIDE_BUY

            print(f'\n{symbol[:-4]} Price : {symbol_price} | Position : {main_order} | Size : {amount} {symbol[:-4]} | ' +
                f'Available Balance {available_balance} | Limit Price : {price} | TP : {take_profit} | SL : {stop_loss}')

            try:
                orders_each['orders'] = {}
                order_main = client.futures_create_order(
                    symbol=symbol,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    side=main_order,
                    positionSide="BOTH",
                    quantity=amount,
                    reduceOnly='false',
                    timeInForce="GTC",
                    price=price,
                )

                main_order_id = order_main['orderId']
                order_time = datetime.fromtimestamp(
                    order_main['updateTime']/1000).strftime("%Y-%m-%d_%H%M%S")

                print(f"\n{main_order_id} | LIMIT order placed successfully for {api_data['binance'][i]['api_key']}")
                orders_each['orders']['main_order'] = order_main

            except Exception as e:
                raise Exception(f"Error LIMIT Order | {type(e).__name__} | {e.args[0] if e.args else ''}")


            sleep(2)
            try:
                order_take_profit = client.futures_create_order(
                    symbol=symbol,
                    side=tp_sl_order,
                    positionSide="BOTH",
                    type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                    timeInForce="GTE_GTC",
                    quantity=amount,
                    stopPrice=take_profit,
                    workingType="MARK_PRICE",
                    reduceOnly='true',
                )

                print(f"\n{order_take_profit['orderId']} | TAKE PROFIT order placed successfully for {api_data['binance'][i]['api_key']}")
                orders_each['orders']['take_profit_order'] = order_take_profit

            except Exception as e:
                for _ in range(3):
                    try:
                        client.futures_cancel_order(
                            symbol=symbol,
                            orderId=main_order_id
                        )

                        print(f"\nLIMIT order [{main_order_id}] canceled successfully for {api_data['binance'][i]['api_key']}")
                        break
                    except Exception as exc:
                        print(exc)
                        sleep(2)

                raise Exception(f"Error placing take profit order: {e}")
            
            try:
                order_stop_loss = client.futures_create_order(
                    symbol=symbol,
                    side=tp_sl_order,
                    positionSide="BOTH",
                    type=FUTURE_ORDER_TYPE_STOP_MARKET,
                    timeInForce="GTE_GTC",
                    quantity=amount,
                    stopPrice=stop_loss,
                    workingType="MARK_PRICE",
                    reduceOnly='true',
                )

                print(f"\n{order_stop_loss['orderId']} | STOP LOSS order placed successfully for {api_data['binance'][i]['api_key']}")
                orders_each['orders']['stop_loss_order'] = order_stop_loss

            except Exception as e:
                for _ in range(3):
                    try:
                        client.futures_cancel_order(
                            symbol=symbol,
                            orderId=main_order_id
                        )

                        print(f"\nLIMIT order [{main_order_id}] canceled successfully for {api_data['binance'][i]['api_key']}")
                        break
                    except Exception as exc:
                        print(exc)
                        sleep(2)

                raise Exception(f"Error placing stop loss order: {e}")
            
            order_path = os.path.join(cwd, 'orders', f"order_{api_data['binance'][i]['api_key']}_{main_order_id}_{order_time}.json")
            json_object = json.dumps(orders, indent=4)
            with open(order_path, "w", encoding='utf-8-sig') as outfile:
                outfile.write(json_object)

            orders[orders_each['binance']['api_key']]  =  orders_each

    except Exception as e:
        print(f"\nLine : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}")
        orders['status'] = 'error'
        orders['error'] = str(e)
        order_path = os.path.join(cwd, 'orders', f"error_{order_time}.json")
        json_object = json.dumps(orders, indent=4)

        with open(order_path, "w", encoding='utf-8-sig') as outfile:
            outfile.write(json_object)

def loadConfig():
    try:
        with open('config.json') as f:
            global configs
            configs = json.load(f)
            print(configs)
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise e


if __name__ == '__main__':
    try:
        setOdersList()

    except Exception as e:
        print(f"\nLine : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}")
