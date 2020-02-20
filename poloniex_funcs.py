import hmac 
import requests
import urllib
import hashlib
import json
import time

import database_funcs as _db

# poloniex config
from poloniex_config import API_KEY
from poloniex_config import SECRET

TRADING_URL = "https://poloniex.com/tradingApi"

def api_post(logger, req, retries):

    while (retries != 0):
        retries -= 1
        time.sleep(1)
        req['nonce'] = int(time.time()*1000)
        post_data = urllib.parse.urlencode(req)
        sign = hmac.new(SECRET, bytes(post_data, 'latin-1'),
                        hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': API_KEY
        }

        try:
            ret = requests.post(TRADING_URL, data=req,
                                headers=headers, timeout=10)
            if ret.status_code != 200:
                logger.error("Error code:{}".format(ret))
                if retries == 0:
                    break
            else:
                return ret.json()
        except requests.exceptions.HTTPError as errh:
            logger.error("Error HTTPError:{}".format(errh))
            if retries == 0:
                break

        except requests.exceptions.ConnectionError as errc:
            logger.error("Error ConnectionError:{}".format(errc))
            if retries == 0:
                break
        except requests.exceptions.Timeout as errt:
            logger.error("Error Timeout:{}".format(errt))
            if retries == 0:
                break

        except requests.exceptions.RequestException as err:
            logger.error("Error RequestException:{}".format(err))
            if retries == 0:
                break

    return False

#semaphore is necessary
# https://github.com/dutu/poloniex-api-node/issues/26


def get_open_orders(semaphore, logger, currency_pair):
    with semaphore:
        req = {}
        req['command'] = "returnOpenOrders"
        req['currencyPair'] = currency_pair
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


def cancel_order(semaphore, logger, order_number):
    with semaphore:
        req = {}
        req['command'] = "cancelOrder"
        req['orderNumber'] = order_number
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


def get_complete_available_balances(logger):
    req = {} 
    req['command'] = "returnCompleteBalances"
    req['nonce'] = int(time.time()*1000)
    return api_post(logger,req,3)

def get_available_balances(semaphore, logger):
    with semaphore:
        req = {}
        req['command'] = "returnBalances"
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


def buy(semaphore, logger, currency_pair, rate, amount):
    with semaphore:
        req = {}
        req['command'] = "buy"
        req['currencyPair'] = currency_pair
        req['rate'] = rate
        req['amount'] = amount
        req['postOnly'] = 1
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


def buy_now(semaphore, logger, remote_data_base_config, currency_pair, time_frame, rate, amount):
    retries = 12
    order = False
    while (retries > 0):
        retries -= 1
        with semaphore:
            req = {}
            req['command'] = "buy"
            req['currencyPair'] = currency_pair
            req['rate'] = rate
            req['amount'] = amount
            req['immediateOrCancel'] = 1
            req['fillOrKill'] = 1
            req['nonce'] = int(time.time()*1000)
            order = api_post(logger, req, 1)
        if order == False:
            time.sleep(10)
            continue
        if "orderNumber" in order and int(order["orderNumber"]) > 1:
            return order
        time.sleep(5)
        ticket = _db.getLastTicketFromDB(
            logger, remote_data_base_config, currency_pair, time_frame)
        logger.debug("try to buy last ticket:{}".format(ticket))
        if ticket:
            rate = ticket['lowestAsk']
    return order


def sell_now_secure(semaphore, logger, remote_data_base_config, currency_pair, time_frame, rate, amount, rate_limit):
    retries = 48 * 10
    order = False
    total_amount_in_usd = amount * rate
    logger.debug("sell total_amount_in_usd:{}".format(total_amount_in_usd))
    amount_item_in_usd = 500.0
    logger.debug("amount_item_in_usd:{}".format(amount_item_in_usd))
    num_items = total_amount_in_usd / amount_item_in_usd
    logger.debug("sell num_items:{}".format(num_items))
    if num_items  > 2:
        amount_item = amount / float(num_items)
        logger.debug("sell amount_item:{}".format(amount_item))
    else:
        amount_item = amount
        logger.debug("sell amount_item:{} equal to amount".format(amount_item))



    while (retries > 0):
        retries -= 1
        with semaphore:
            req = {}
            req['command'] = "sell"
            req['currencyPair'] = currency_pair
            req['rate'] = rate
            req['amount'] = amount_item
            req['immediateOrCancel'] = 1
            req['fillOrKill'] = 1
            req['nonce'] = int(time.time()*1000)
            order = api_post(logger, req, 1)

        if order == False:
            time.sleep(2)
            continue

        if "orderNumber" in order and int(order["orderNumber"]) > 1:
            logger.debug("sell order ok:{}".format(order))
            logger.debug("sell amount_item:{}".format(amount_item))
            amount -= amount_item
            logger.debug("sell amount remain{}".format(amount))
            amount_in_usd = amount * rate
            logger.debug("sell amount remain in usd{}".format(amount_in_usd))
            if amount_in_usd < 10.0:
                return order
            else:
                logger.debug("sell amount remain in usd is bigger than 10 usd{}".format(amount_in_usd))
                pass
                
            
        time.sleep(1)
        ticket = _db.getLastTicketFromDB(
            logger, remote_data_base_config, currency_pair, time_frame)
        logger.debug("try to sell last ticket:{}".format(ticket))
        if ticket:
            rate = ticket['highestBid'] - (ticket['highestBid']*0.001)
            logger.debug("new rate:{}".format(rate))
            if rate < rate_limit:
                logger.debug(
                    "end selling rate lower than rate_limit:{}".format(rate_limit))
                return False

    return order


def sell_now(semaphore, logger, remote_data_base_config, currency_pair, time_frame, rate, amount):
    retries = 48
    order = False
    while (retries > 0):
        retries -= 1
        with semaphore:
            req = {}
            req['command'] = "sell"
            req['currencyPair'] = currency_pair
            req['rate'] = rate
            req['amount'] = amount
            req['immediateOrCancel'] = 1
            req['fillOrKill'] = 1
            req['nonce'] = int(time.time()*1000)
            order = api_post(logger, req, 1)

        if order == False:
            time.sleep(10)
            continue

        if "orderNumber" in order and int(order["orderNumber"]) > 1:
            return order
        time.sleep(4)
        ticket = _db.getLastTicketFromDB(
            logger, remote_data_base_config, currency_pair, time_frame)
        logger.debug("try to sell last ticket:{}".format(ticket))
        if ticket:
            rate = ticket['highestBid']

    return order


def sell(semaphore, logger, currency_pair, rate, amount):
    with semaphore:
        req = {}
        req['command'] = "sell"
        req['currencyPair'] = currency_pair
        req['rate'] = rate
        req['postOnly'] = 1
        req['amount'] = amount
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


def get_trade_history(semaphore, logger, currency_pair):
    with semaphore:
        now = int(time.time())
        req = {}
        req['command'] = "returnTradeHistory"
        req['start'] = now - (86400*90)
        req['end'] = now - (1)
        req['limit'] = 6000
        req['currencyPair'] = currency_pair
        req['nonce'] = int(time.time()*1000)
        return api_post(logger, req, 3)


