
import json
import time
import poloniex_funcs as  _poloniex
from datetime import datetime
import database_funcs as _db
import purchase_operations_funcs as _purchase

def get_last_purchase_trade_operations (semaphore,logger,currency_pair):
    trade_history = _poloniex.get_trade_history (semaphore,logger,currency_pair)#suppose sorter 
    if trade_history == False:
        return False 
    last_purchase_trade_operations = [] 
    for i,trade in enumerate(trade_history):
        if trade['type'] ==  "sell":
            return last_purchase_trade_operations
        else:
            last_purchase_trade_operations.append(trade)
    return last_purchase_trade_operations  

def get_last_purchase_operations (semaphore,logger,currency_pair):
    last_purchase_operations = [] 
    last_purchase_trade_operations = get_last_purchase_trade_operations (semaphore,logger,currency_pair)
    if last_purchase_trade_operations == False or last_purchase_trade_operations == [] :
        return last_purchase_operations
    else:
        for trade in last_purchase_trade_operations:
            date_ts = trade['date'] 
            rate = float(trade['rate'])
            fee = float(trade['fee'])
            total = float(trade['total'])
            amount = float(trade['amount'])
            epoch = datetime.strptime(date_ts,'%Y-%m-%d %H:%M:%S').timestamp()
            last_purchase_operations.append((rate,epoch,fee,total,amount))
    return last_purchase_operations

def try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,output_rsi,model,mean_purchase_prices):
  
    ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
    logger.debug("try to buy last ticket:{}".format(ticket))
    if ticket:
        last = ticket['last'] 
        lowestAsk = ticket['lowestAsk']
        purchase_loss = (lowestAsk/last) -1.0
        purchase_price = lowestAsk
        
        initial_amount_to_buy_in_base = float(model['initial_amount_to_buy_in_base'])
        min_amount_to_buy_in_base = float(model['min_amount_to_buy_in_base'])
        max_amount_to_buy_in_base = float(model['max_amount_to_buy_in_base'])
        logger.debug("purchase_price lowestAsk:{}".format(purchase_price))
        logger.debug("purchase_loss:{}".format(purchase_loss))
        logger.debug("initial amount to buy in base:{}".format(initial_amount_to_buy_in_base))
        logger.debug("min_amount_to_buy_in_base:{}".format(min_amount_to_buy_in_base))
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        purchase_operations = get_last_purchase_operations (semaphore,logger,currency_pair)
        logger.debug("purchase_operations:{}".format(purchase_operations))
        if len(purchase_operations) == 0:
            amount_to_buy_in_base = initial_amount_to_buy_in_base
            amount_to_buy_in_quote  = amount_to_buy_in_base / purchase_price
            logger.debug("intial amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
            logger.debug("amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
            current_mean_price = purchase_price
        else:
            current_mean_price = _purchase.getCurrentRealMeanPrice(purchase_operations)
            logger.debug("current_mean_price:{}".format(current_mean_price))
            delta_price_over_mean = (purchase_price/current_mean_price) - 1.0
            logger.debug("delta_price_over_mean:{}".format(delta_price_over_mean))
            if delta_price_over_mean > -0.002:
                logger.debug("purchase_price:{}".format(purchase_price))
                logger.debug("current_mean_price:{}".format(current_mean_price))
                logger.debug("aborted buy not improve mean")
                logger.debug("delta_price_over_mean:{}".format(delta_price_over_mean))
                return
            if model['r_mode'] == 1:
                r_mod = model['r'] * len(purchase_operations)
            else:
                r_mod =  model['r']
            amount_to_buy_in_quote = _purchase.get_amount_to_buy_in_quote(logger,purchase_operations,purchase_price,initial_amount_to_buy_in_base,min_amount_to_buy_in_base,max_amount_to_buy_in_base,r_mod)
            amount_to_buy_in_base = amount_to_buy_in_quote * purchase_price
            logger.debug("we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
            logger.debug("we are gointo buy in base:{}".format(amount_to_buy_in_base))

        current_amount_invested = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("current_amount_invested:{}".format(current_amount_invested))
        available_balances = _poloniex.get_available_balances(semaphore,logger)
        if available_balances == False:
            logger.debug("Error getting available_balances:{}".format(available_balances))
            return False
        currencies = currency_pair.split("_") 
        base_currency = currencies[0]
        quote_currency = currencies[1]     
        base_balance = float(available_balances[base_currency])
        quote_balance = float(available_balances[quote_currency])
        logger.debug("base_balance:{}".format(base_balance)) 
        logger.debug("quote_balance:{}".format(quote_balance))
        if amount_to_buy_in_base < 5.0:
            logger.debug("aborted buy by amount_to_buy_in_base")
            return
        if base_balance <= 10*min_amount_to_buy_in_base:
            logger.debug("aborted buy by low balance")
            logger.debug("base_balance:{}".format(base_balance))
            return

        if base_balance <=  amount_to_buy_in_base  :
            amount_to_buy_in_base = base_balance
            amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price
            logger.debug("low balance revisited we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
            logger.debug("low balance revisited we are gointo buy in basde:{}".format(amount_to_buy_in_base))

        if purchase_loss < 0.015:
            response = _poloniex.buy_now(semaphore,logger,remote_data_base_config,currency_pair,time_frame,purchase_price,amount_to_buy_in_quote) 
        else:
            purchase_price = last
            logger.debug("new purchase_price:{} try to open order".format(purchase_price))
            response = _poloniex.buy(semaphore,logger,currency_pair,purchase_price,amount_to_buy_in_quote)
        logger.debug("response to buy:{}".format(response))
        if response != False:
            if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                time.sleep(10)
                purchase_operations = get_last_purchase_operations (semaphore,logger,currency_pair)
                logger.debug("updated purchase_operations:{}".format(purchase_operations))
                current_mean_price = _purchase.getCurrentRealMeanPrice(purchase_operations)
                logger.debug("new current_mean_price:{}".format(current_mean_price))
                delta_price_over_mean = (purchase_price/current_mean_price) - 1.0
                logger.debug("new delta_price_over_mean:{}".format(delta_price_over_mean))
                mean_purchase_prices.append(current_mean_price)
                _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'buy',purchase_price,amount_to_buy_in_quote,amount_to_buy_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_price,output_rsi,int(response['orderNumber']),json.dumps(response))



def try_to_sell_NOW (semaphore,logger,remote_data_base_config,currency_pair,increment,time_frame,output_rsi,amount_to_sell,mean_purchase_prices):
 
    ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
    logger.debug("try to sell last ticket NOW:{}".format(ticket))
    if ticket:
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        if mean_purchase_prices == []:
            current_mean_purchase_price = 0
        else:
            current_mean_purchase_price = mean_purchase_prices[-1] 
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        logger.debug("current_mean_purchase_price:{}".format(current_mean_purchase_price))
        amount_in_base = amount_to_sell * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(amount_to_sell))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        sell_price_limit = sell_price  - (sell_price*0.005)
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_price_limit:{}".format(sell_price_limit))
        response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
        if response != False:
            if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))

def try_to_sell_UNSOLD (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,candle_rsi,output_rsi,amount_to_sell,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,sos_rate,mean_purchase_prices):
 
    ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
    logger.debug("try to sell last ticket:{}".format(ticket))
    if ticket:
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        if mean_purchase_prices == []:
            current_mean_purchase_price = 0
            logger.error("zero current_mean_purchase_price:{}".format(current_mean_purchase_price))
            return
        else:
            current_mean_purchase_price = mean_purchase_prices[-1] 
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        logger.debug("current_mean_purchase_price:{}".format(current_mean_purchase_price))
        if current_mean_purchase_price == 0:
            logger.error("zero current_mean_purchase_price:{}".format(current_mean_purchase_price))
            return
        amount_in_base = amount_to_sell * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(amount_to_sell))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        current_rate_benefit = (sell_price/current_mean_purchase_price) - 1.0
        logger.debug("current_rate_benefit:{}".format(current_rate_benefit))
        abs_rate_loss = abs(current_rate_benefit/(sell_loss+0.0001))
        logger.debug("abs rate_loss:{}".format(abs_rate_loss))
        if always_win:
            if current_rate_benefit > float(sos_rate):
                sell_price_limit = sell_price  - (sell_price*0.005)
                logger.debug("sell_price:{}".format(sell_price))
                logger.debug("sell_price_limit:{}".format(sell_price_limit))
                response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
                if response != False:
                    if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                        _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))
            else:
                logger.debug("current rate benefit not enough to UNSOLD sell:{}".format(current_rate_benefit))
        else:
            if candle_rsi > (output_rsi / 1000.0):
                sell_price_limit = sell_price  - (sell_price*0.005)
                logger.debug("sell_price:{}".format(sell_price))
                logger.debug("sell_price_limit:{}".format(sell_price_limit))
                response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
                if response != False:
                    if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                        _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))
            else:
                logger.debug("always win is false but candle_rsi is low to UNSOLD sell :{}".format(candle_rsi))

def try_to_sell_SOS (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,candle_rsi,output_rsi,amount_to_sell,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,sos_rate,mean_purchase_prices):
 
    ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
    logger.debug("try to sell last ticket:{}".format(ticket))
    if ticket:
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        if mean_purchase_prices == []:
            current_mean_purchase_price = 0
        else:
            current_mean_purchase_price = mean_purchase_prices[-1] 
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        logger.debug("current_mean_purchase_price:{}".format(current_mean_purchase_price))
        amount_in_base = amount_to_sell * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(amount_to_sell))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        purchase_operations = get_last_purchase_operations (semaphore,logger,currency_pair)
        logger.debug("purchase_operations:{}".format(purchase_operations))
        total_amount_invested_in_base = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
        rate_amount = total_amount_invested_in_base / max_amount_to_buy_in_base
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        logger.debug("rate_amount:{}".format(rate_amount))
        current_percent_benefit = _purchase.getCurrentPercentBenefit(purchase_operations,sell_price)
        logger.debug("current_percent_benefit:{}".format(current_percent_benefit))
        current_rate_benefit = current_percent_benefit/100.0
        logger.debug("current_rate_benefit:{}".format(current_rate_benefit))
        total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
        logger.debug("total_current_base_benefit:{}".format(total_current_base_benefit))
        abs_rate_loss = abs(current_rate_benefit/(sell_loss+0.0001))
        logger.debug("abs rate_loss:{}".format(abs_rate_loss))
        if always_win:
            if current_rate_benefit > float(sos_rate):
                sell_price_limit = sell_price  - (sell_price*0.005)
                logger.debug("sell_price:{}".format(sell_price))
                logger.debug("sell_price_limit:{}".format(sell_price_limit))
                response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
                if response != False:
                    if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                        _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))
            else:
                logger.debug("current rate benefit not enough to SOS sell:{}".format(current_rate_benefit))
        else:
            if candle_rsi > (output_rsi / 1000.0):
                sell_price_limit = sell_price  - (sell_price*0.005)
                logger.debug("sell_price:{}".format(sell_price))
                logger.debug("sell_price_limit:{}".format(sell_price_limit))
                response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
                if response != False:
                    if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                        _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))
            else:
                logger.debug("always win is false but candle_rsi is low to SOS sell :{}".format(candle_rsi))


def try_to_sell (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,output_rsi,amount_to_sell,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,mean_purchase_prices):
  
    ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
    logger.debug("try to sell last ticket:{}".format(ticket))
    if ticket:
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        if mean_purchase_prices == []:
            current_mean_purchase_price = 0
        else:
            current_mean_purchase_price = mean_purchase_prices[-1] 
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        logger.debug("current_mean_purchase_price:{}".format(current_mean_purchase_price))
        amount_in_base = amount_to_sell * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(amount_to_sell))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        purchase_operations = get_last_purchase_operations (semaphore,logger,currency_pair)
        logger.debug("purchase_operations:{}".format(purchase_operations))
        total_amount_invested_in_base = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
        rate_amount = total_amount_invested_in_base / max_amount_to_buy_in_base
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        logger.debug("rate_amount:{}".format(rate_amount))
        current_percent_benefit = _purchase.getCurrentPercentBenefit(purchase_operations,sell_price)
        logger.debug("current_percent_benefit:{}".format(current_percent_benefit))
        current_rate_benefit = current_percent_benefit/100.0
        logger.debug("current_rate_benefit:{}".format(current_rate_benefit))
        total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
        logger.debug("total_current_base_benefit:{}".format(total_current_base_benefit))
        abs_rate_loss = abs(current_rate_benefit/(sell_loss+0.0001))
        logger.debug("abs rate_loss:{}".format(abs_rate_loss))
        '''
        if always_win:
            if (current_rate_benefit < min_current_rate_benefit):
                logger.debug("aborted sell i want to win always:{}  and current benefit:{}".format(min_current_rate_benefit,current_rate_benefit))
                return
        '''
        if True: #in not sos mode always win is always true  
            if (current_rate_benefit < min_current_rate_benefit):
                logger.debug("aborted sell i want to win always:{}  and current benefit:{}".format(min_current_rate_benefit,current_rate_benefit))
                return
        #to avoid splitting the sell always sell_now_secure  with highestBid
        #splitting the sell can cause some errors getting current mean price
        '''
        if sell_loss < 0.006 or abs_rate_loss>4.0 or rate_amount > 0.5 :
      
           
            rate_secure =  current_rate_benefit * 0.1   
            sell_price_limit = sell_price  - (sell_price*rate_secure)
            logger.debug("sell_price:{}".format(sell_price))
            logger.debug("sell_price_limit:{}".format(sell_price_limit))
            response = sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
        
        else:
            sell_price = last
            logger.debug("new sell_price:{} try to open order".format(sell_price))
            response = sell(semaphore,logger,currency_pair,sell_price,amount_to_sell)
        '''
        rate_secure =  current_rate_benefit * 0.1   
        sell_price_limit = sell_price  - (sell_price*rate_secure)
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_price_limit:{}".format(sell_price_limit))
        response = _poloniex.sell_now_secure(semaphore,logger,remote_data_base_config,currency_pair,time_frame,sell_price,amount_to_sell,sell_price_limit)
        if response != False:
            if 'orderNumber' in response and int(response['orderNumber']) > 0 :
                _db.logInsertOrder(logger,remote_data_base_config,currency_pair,'sell',sell_price,amount_to_sell,amount_in_base,increment,"neighbors","1",ticket['last'],ticket['highestBid'],ticket['lowestAsk'],current_mean_purchase_price,output_rsi,int(response['orderNumber']),json.dumps(response))

def manage_open_orders(semaphore,logger,currency_pair,remote_data_base_config,model,time_frame,base_currency,quote_currency,output_rsi,close,increment,mean_purchase_prices):
    open_orders = _poloniex.get_open_orders(semaphore,logger,currency_pair)
    logger.debug("open_orders response:{}".format(open_orders)) 
    if open_orders == False:
        logger.error("Error getting open orders")
        return False
    if open_orders == []:
        logger.debug("There is no open open orders OK!.") 
        return True
    else:
        logger.debug("There is  open orders i'll try to cancel them.") 
        for open_order in open_orders:
            logger.debug("open order:{}".format(open_order))
            if not 'orderNumber' in open_order:
                logger.error("Error in open_order orderNumber")
                return False
            if int(open_order['orderNumber']) < 1:
                logger.error("Error in open_order orderNumber less than 1")
                return False
        
            if 'date' in open_order:
                order_datetime = datetime.strptime(open_order['date'] ,'%Y-%m-%d %H:%M:%S')
                seconds_diff = (datetime.now() - order_datetime).total_seconds()
                logger.debug("seconds_diff:{}".format(seconds_diff))
            else:
                logger.error("Error in open_order date")
                return False
            if 'type' in open_order:
                if open_order['type'] == 'buy':
                    if seconds_diff > 15 * 60:
                        retval = _poloniex.cancel_order(semaphore,logger,open_order['orderNumber'])
                        logger.debug("cancel order response:{}".format(retval))
                        if retval != False and "success" in retval and int(retval['success']) == 1:
                            _db.logInsertCancelOrder(logger,remote_data_base_config,currency_pair,"buy","neighbors","1",int(open_order['orderNumber']),json.dumps(retval))
                    else:
                        #if ticket has changed cancel current order and add a new one 
                        open_order_purchase_price = float(open_order['rate'])
                        logger.debug("open_order_purchase_price:{}".format(open_order_purchase_price))
                        ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
                        if ticket == False:
                            logger.debug("Error getting last ticket to calculate new open_order_purchase_price:{}".format(ticket))
                            return False
                        last = float(ticket['last'])
                        logger.debug("last:{}".format(last))
                        if last != open_order_purchase_price: 
                            logger.debug("the last value has changed now:{}  before:{} ".format(last,open_order_purchase_price))
                            retval = _poloniex.cancel_order(semaphore,logger,open_order['orderNumber'])
                            logger.debug("response to cancel_order:{}".format(retval))
                            delta_change = (last/open_order_purchase_price) - 1.0
                            if retval != False and "success" in retval and int(retval['success']) == 1:
                                logger.debug("cancel order response ok:{}".format(retval))
                                _db.logInsertCancelOrder(logger,remote_data_base_config,currency_pair,"buy","neighbors","1",int(open_order['orderNumber']),json.dumps(retval))
                                time.sleep(2)
                                purchase_price = last
                                if delta_change < 0.005:
                                    logger.debug("new purchase_price:{} try to open order".format(purchase_price))
                                    try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,output_rsi,model,mean_purchase_prices)
                                else:
                                    logger.debug("delta change:{} too high. The price is not as good as when shouldIInvest was yes.".format(delta_change))

                if  open_order['type'] == 'sell':
                    if seconds_diff > 40 * 60:
                        retval = _poloniex.cancel_order(semaphore,logger,open_order['orderNumber'])
                        logger.debug("cancel order response:{}".format(retval))
                        if retval != False  and "success" in retval and int(retval['success']) == 1:
                            _db.logInsertCancelOrder(logger,remote_data_base_config,currency_pair,"sell","neighbors","1",int(open_order['orderNumber']),json.dumps(retval))
                    else:
                        #if ticket has changed cancel current order and add a new one  
                        open_order_sell_price = float(open_order['rate']) 
                        logger.debug("open_order_sell_price:{}".format(open_order_sell_price))
                        ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
                        if ticket == False:
                            logger.debug("Error getting last ticket to calculate new open_order_sell_price:{}".format(ticket))
                            return False
                        last = float(ticket['last'])
                        logger.debug("last:{}".format(last))
                        if last != open_order_sell_price: 
                            logger.debug("the last value has changed now:{}  before:{} ".format(last,open_order_sell_price))
                            retval = _poloniex.cancel_order(semaphore,logger,open_order['orderNumber'])
                            logger.debug("response to cancel_order:{}".format(retval))
                            if retval != False and  "success" in retval and int(retval['success']) == 1:
                                _db.logInsertCancelOrder(logger,remote_data_base_config,currency_pair,"sell","neighbors","1",int(open_order['orderNumber']),json.dumps(retval))
                                time.sleep(2)
                                sell_price = last
                                logger.debug("new sell_price:{} try to open order".format(sell_price))
                                available_balances = _poloniex.get_available_balances(semaphore,logger)
                                if available_balances == False:
                                    logger.debug("Error getting available_balances:{}".format(available_balances))
                                    return False
                                base_balance = float(available_balances[base_currency])
                                quote_balance = float(available_balances[quote_currency]) 
                                try_to_sell (semaphore,logger,remote_data_base_config,currency_pair,close,increment,time_frame,output_rsi,quote_balance,model['always_win'] ,model['min_current_rate_benefit'] ,model['max_amount_to_buy_in_base'],base_balance,mean_purchase_prices )
        return False