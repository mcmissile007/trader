import pandas as pd
from datetime import datetime
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import glob
import random

import multiprocessing

#currency_codes dicts
from currency_codes import r_codes


from database_config import remote_data_base_config

import math_funcs as _mth
import poloniex_funcs as  _poloniex
import database_funcs as _db
import invest_funcs as _invest
import trader_funcs as _trader
import aux_funcs as _aux
import matrix_funcs as _matrix


def main(semaphore,model,global_quote_percent):

    last_signals = {}
    time_frame = 300
    time_from_genesis = 0
    genesis_th = 24 * 3600  
    currency_pair = model['currency_pair']
    always_win = model['always_win'] 
    rsi_mode = model['rsi_mode'] 
    min_current_rate_benefit = model['min_current_rate_benefit'] 
    max_amount_to_buy_in_base = model['max_amount_to_buy_in_base']
    sleep_time = model['sleep_time']  
    initial_amount_to_buy_in_base = model['initial_amount_to_buy_in_base'] 
    currencies = currency_pair.split("_") 
    base_currency = currencies[0]
    quote_currency = currencies[1] 
    output_rsi = int(model['ben_field'].split('_')[1])   
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(currency_pair)
    log_file_name = model['log_file_name'] 
    filename =  "./logs/" + log_file_name + "." + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #logging.getLogger("urllib3").setLevel(logging.WARNING)
    #logging.getLogger("requests").setLevel(logging.WARNING)
    logger.info("START")
    logger.info("log_file_name:{}".format(log_file_name))
    logger.info("currency_pair:{}".format(currency_pair))
    logger.info("amount_to_buy in base:{}".format(initial_amount_to_buy_in_base))
    logger.info("model:{}".format(model))
    possible_open_order = True
    mean_purchase_prices = []
    _matrix.send("Greetings professor Falken. Let's play {0} with initial_amount_to_buy_in_base {1} ".format(currency_pair,initial_amount_to_buy_in_base)) 
 
    while (True):
        
        time.sleep(0.5)
        send_state = False
        timeframes = _aux.decideCurrentTimeFrame(last_signals)
        if timeframes == []:
            continue
        logger.debug("Start analyzing")    
        now = int(time.time())
       
        if now % time_frame != 0:
            logger.debug("Error now time:%d",now)
            continue
        time.sleep(sleep_time) # wait to have the last candle and balances in database
        logger.debug("analyzing:%s***",str(datetime.now()))
        now_datetime = datetime.now()
        if now_datetime.hour == 7 and now_datetime.minute == 30:
            send_state = True
        if now_datetime.hour == 13 and now_datetime.minute == 30:
            send_state = True
        if now_datetime.hour == 21 and now_datetime.minute == 30:
            send_state = True
        if now - time_from_genesis > genesis_th:
            logger.debug("reading learning dataframe: %s ",str(datetime.now()))
            data_files = glob.glob("data/*" + currency_pair + "*.pkl")
            if data_files == []:
                logger.error("No learning data file for this currency:{}".format(currency_pair))
                time_from_genesis = 0
                time.sleep(60)
                continue
            files = [] 
            for data_file in data_files:
                file_name =  data_file.split('/')[1]
                epoch = int(file_name.split('_')[0])
                diff_seconds = now - epoch
                files.append((file_name,diff_seconds))
            files.sort(key=lambda x : x[1] )
            file_to_read = "data/" + files[0][0]
            logger.debug("file_to_read:{}".format(file_to_read)) 
            learning_df = pd.read_pickle(file_to_read)
            time_from_genesis = now 
            logger.debug ("learning dataframe head:{}".format(learning_df.head()))
            logger.debug ("learning dataframe tail:{}".format(learning_df.tail()))

            sma50_delta_mean = learning_df.sma50_delta.mean()
            sma50_delta_std = learning_df.sma50_delta.std()
            ema26_delta_mean = learning_df.ema26_delta.mean()
            ema26_delta_std = learning_df.ema26_delta.std()
            ema13_delta_mean = learning_df.ema13_delta.mean()
            ema13_delta_std = learning_df.ema13_delta.std()
            roc0_mean = learning_df.roc0.mean()
            roc0_std = learning_df.roc0.std()
            roc1_mean = learning_df.roc1.mean()
            roc1_std = learning_df.roc1.std()
            roc3_mean = learning_df.roc3.mean()
            roc3_std = learning_df.roc3.std()
            roc6_mean = learning_df.roc6.mean()
            roc6_std = learning_df.roc6.std()
            roc12_mean = learning_df.roc12.mean()
            roc12_std = learning_df.roc12.std()
            roc24_mean = learning_df.roc24.mean()
            roc24_std = learning_df.roc24.std()
            roc48_mean = learning_df.roc48.mean()
            roc48_std = learning_df.roc48.std()
            roc72_mean = learning_df.roc72.mean()
            roc72_std = learning_df.roc72.std()
            roc288_mean = learning_df.roc288.mean()
            roc288_std = learning_df.roc288.std()
            trix_mean = learning_df.trix.mean()
            trix_std = learning_df.trix.std()
            rsi_mean = learning_df.rsi.mean()
            rsi_std = learning_df.rsi.std()
            macd_mean = learning_df.macd.mean()
            macd_std = learning_df.macd.std()
            histogram_mean = learning_df.histogram.mean()
            histogram_std = learning_df.histogram.std()
            continue

        max_num_of_results = 300
        last_candles = _db.getLastCandlesFromTickets(logger,remote_data_base_config,currency_pair,time_frame,now,max_num_of_results)
        if last_candles  == False:
            logger.debug("error getting candles from db.")
            continue
        candles_df = pd.DataFrame(last_candles)
        candles_df['tm'] = candles_df['date'].apply(datetime.fromtimestamp) 
        candles_df['roc0'] =  (candles_df['close']/candles_df['open']) - 1.0
        candles_df['roc1'] = candles_df.close.pct_change(periods=1)
        candles_df['roc3'] = candles_df.close.pct_change(periods=3)
        candles_df['roc6'] = candles_df.close.pct_change(periods=6) 
        candles_df['roc12'] = candles_df.close.pct_change(periods=12) 
        candles_df['roc24'] = candles_df.close.pct_change(periods=24)
        candles_df['roc48'] = candles_df.close.pct_change(periods=48)
        candles_df['roc72'] = candles_df.close.pct_change(periods=72)
        candles_df['roc288'] = candles_df.close.pct_change(periods=288)
        candles_df['body'] = (candles_df['close'] - candles_df['open']).abs()/(candles_df['high'] - candles_df['low'])
        candles_df['sma50'] = candles_df['close'].rolling(50,min_periods=50).mean() 
        candles_df['ema26'] = candles_df['close'].ewm(span=26,min_periods=26).mean() 
        candles_df['ema13'] = candles_df['close'].ewm(span=13,min_periods=13).mean()
        candles_df['ex2'] = candles_df['ema13'].ewm(span=13,min_periods=13).mean()
        candles_df['ex3'] = candles_df['ex2'].ewm(span=13,min_periods=13).mean()
        candles_df['trix'] = (candles_df['ex3']/candles_df['ex3'].shift(1))  - 1.0  
        candles_df['macd'] =  candles_df['ema13'] - candles_df['ema26']
        candles_df['signal'] = candles_df['macd'].ewm(span=9,min_periods=9).mean()
        candles_df['histogram'] = candles_df['macd'] - candles_df['signal']
        candles_df['rsi']  = _mth.get_rsi(candles_df['close'],14)
        candles_df['rsi_14']  = _mth.get_rsi(candles_df['close'],14)
        candles_df['rsi_28']  = _mth.get_rsi(candles_df['close'],28)
        candles_df['rsi_56']  = _mth.get_rsi(candles_df['close'],56)
        candles_df['sma50_delta'] = (candles_df.close - candles_df.sma50)/candles_df.sma50 
        candles_df['sma50_delta_z'] = (candles_df.sma50_delta - sma50_delta_mean)/sma50_delta_std
        candles_df['ema26_delta'] = (candles_df.close - candles_df.ema26)/candles_df.ema26
        candles_df['ema26_delta_z'] = (candles_df.ema26_delta - ema26_delta_mean)/ema26_delta_std
        candles_df['ema13_delta'] = (candles_df.close - candles_df.ema13)/candles_df.ema13
        candles_df['ema13_delta_z'] = (candles_df.ema13_delta - ema13_delta_mean)/ema13_delta_std
        candles_df['roc1_z'] = (candles_df.roc1 - roc1_mean)/roc1_std
        candles_df['roc3_z'] = (candles_df.roc3 - roc3_mean)/roc3_std
        candles_df['roc6_z'] = (candles_df.roc6 - roc6_mean)/roc6_std
        candles_df['roc12_z'] = (candles_df.roc12 - roc12_mean)/roc12_std
        candles_df['roc24_z'] = (candles_df.roc24 - roc24_mean)/roc24_std
        candles_df['roc48_z'] = (candles_df.roc48 - roc48_mean)/roc48_std
        candles_df['roc72_z'] = (candles_df.roc72 - roc72_mean)/roc72_std
        candles_df['roc288_z'] = (candles_df.roc288 - roc288_mean)/roc288_std
        candles_df['trix_z'] = (candles_df.trix - trix_mean)/trix_std
        candles_df['roc0_z'] = (candles_df.roc0 - roc0_mean)/roc0_std
        candles_df['rsi_z'] = (candles_df.rsi - rsi_mean)/rsi_std
        candles_df['macd_z'] = (candles_df.macd - macd_mean)/macd_std
        candles_df['histogram_z'] = (candles_df.histogram - histogram_mean)/histogram_std

        last_candle_df = candles_df[-1:].copy(deep = True)  
        logger.debug("last:candle:{}".format(last_candle_df.T))
        
        #another process does this task to avoid multiple calls to poloniex getbalance per process
        db_balances = _db.getBalanceFromDB(logger,remote_data_base_config,now)
        logger.debug("db_balances:{}".format(db_balances))
        base_percent = 0.0
        quote_percent = 0.0
        global_quote_percent_from_db = 0.0
        balance_from_db_OK = False
        if db_balances != False:
            balance_from_db_OK = True
            for db_balance in db_balances:
                if db_balance['currency']  == base_currency:
                    base_balance = float(db_balance['amount'])
                    base_percent = float(db_balance['percent'])
                elif db_balance['currency']  == quote_currency:
                    quote_balance = float(db_balance['amount'])
                    quote_percent = float(db_balance['percent'])
                    global_quote_percent_from_db += float(db_balance['percent'])
                else :
                    global_quote_percent_from_db += float(db_balance['percent'])
        else:
            available_balances = _poloniex.get_available_balances(semaphore,logger)
            if available_balances == False:
                logger.debug("Error getting available_balances:{}".format(available_balances))
                continue
            base_balance = float(available_balances[base_currency])
            quote_balance = float(available_balances[quote_currency])
            quote_percent = quote_balance / base_balance
            base_percent = 1.0 - quote_percent
            logger.debug("Balance from poloniex. Something is wrong!!.")
        logger.debug("Base balance:{}".format(base_balance))
        logger.debug("Quote balance:{}".format(quote_balance))
        logger.debug("Base percent:{}".format(base_percent))
        logger.debug("Quote percent:{}".format(quote_percent))
        free_to_buy_by_global_quote = True
        if not balance_from_db_OK:
            if currency_pair == "USDC_BTC": #USDC_BTC always is the first coin to analyze,and always is analyzed
                global_quote_percent.value = 0.0
                logger.debug("global_quote_percent set to 0:{}".format(global_quote_percent.value))
            global_quote_percent.value += quote_percent
            logger.debug("global_quote_percent:{}".format(global_quote_percent.value))
            if quote_percent == 0.0: #still not playing this coin
                logger.debug("quote_percent is 0, free to start a play if no other coin is global_quote_percent")
                time.sleep(10) #wait to other coins to update global_quote_percent
                logger.debug("global_quote_percent updated:{}".format(global_quote_percent.value))
                if global_quote_percent.value > 0.0 :
                    logger.debug("Another coin is playing no free to buy")
                    free_to_buy_by_global_quote = False
                else:
                    logger.debug("No coin is playing free to buy for this reason")
                    free_to_buy_by_global_quote = True
        else:
            global_quote_percent.value = global_quote_percent_from_db
            if quote_percent == 0.0: #still not playing this coin
                if global_quote_percent.value > 0.0 :
                    logger.debug("global_quote_from_db. Another coin is playing no free to buy")
                    free_to_buy_by_global_quote = False
                else:
                    logger.debug("global_quote_from_db. No coin is playing free to buy for this reason")
                    free_to_buy_by_global_quote = True
                     
        logger.debug("global_quote_percent:{}".format(global_quote_percent.value))
        if send_state:
            _matrix.send("Daily report: quote_currency {0} . base_balance {1}. quote_balance {2} . base_percent {3} . quote_percent {4}. global_quote_percent {5} ".format(quote_currency,base_balance,quote_balance,base_percent,quote_percent,global_quote_percent.value))
        
        logger.debug("possible_open_order:{}".format(possible_open_order)) 
        free_to_buy_by_open_order = True
        if possible_open_order:
            retval_manage_open_orders = _trader.simple_manage_open_orders(semaphore,logger,currency_pair,remote_data_base_config,model,time_frame,base_currency,quote_currency,output_rsi,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],mean_purchase_prices,global_quote_percent.value)
            if retval_manage_open_orders == True:
                possible_open_order = False
                free_to_buy_by_open_order = True
            else:
                free_to_buy_by_open_order = False
                #if there is an open order neither buy nor sell
                logger.debug("if there is an open order neither buy nor sell,retval_manage_open_orders:{}".format(retval_manage_open_orders)) 
                continue


        logger.debug("free_to_buy_by_open_order:{}".format(free_to_buy_by_open_order))

        

        free_to_buy = free_to_buy_by_global_quote and free_to_buy_by_open_order
       


        if mean_purchase_prices != []: 
            logger.debug("just for test: last_mean_purchase_price:{}".format(mean_purchase_prices[-1]))
        else:
            mean_purchase = _db.getCurrentMeanPurchaseFromDB(logger,remote_data_base_config,currency_pair)
            if mean_purchase == False:
                logger.debug(" just for test:  Error getting mean_purchase to calculate new current_mean_purchase_price:{}".format(mean_purchase))
            else:
                mean_purchase_price = float(mean_purchase['mean_purchase_price'])
                logger.debug(" just for test: mean_purchase_price from db:{}".format(mean_purchase_price))

    
        ticket = _db.getLastTicketFromDB(logger,remote_data_base_config,currency_pair,time_frame)
        if ticket == False:
            logger.debug("Error getting last ticket to calculate amount_invested:{}".format(ticket))
            continue
        current_rate = float(ticket['last'])
        logger.debug("Last ticket:{}".format(ticket))
        amount_invested_in_base  = quote_balance * current_rate
        logger.debug("amount_invested in base:{}".format(amount_invested_in_base))
        logger.debug("amount to sell in quote currency:{}".format(quote_balance))
        enought_quote_balance = False
        if amount_invested_in_base > 2.0:
            enought_quote_balance = True
        logger.debug("enought_quote_balance:{}".format(enought_quote_balance)) 
        maybe_balance_remains_unsold = False
        if amount_invested_in_base > 4.0:
             logger.debug("verify if balance remains unsold:{}".format(amount_invested_in_base)) 
             purchase_operations = _trader.get_last_purchase_operations (semaphore,logger,currency_pair)
             logger.debug("purchase_operations:{}".format(purchase_operations))
             if len(purchase_operations) == 0:
                 maybe_balance_remains_unsold = True
                 logger.debug("not exist purchase operations alert!:{}".format(maybe_balance_remains_unsold)) 
                 if mean_purchase_prices == []:  
                    mean_purchase = _db.getCurrentMeanPurchaseFromDB(logger,remote_data_base_config,currency_pair)
                    if mean_purchase == False:
                        logger.debug("Error getting mean_purchase to calculate new current_mean_purchase_price:{}".format(mean_purchase))
                        logger.debug("sell immediately to finish the previous operation.")
                        #it's dangerous, do it manually in beta. 
                        #_trader.try_to_sell_NOW(semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,quote_balance,mean_purchase_prices) 
                        continue
                    else:
                        mean_purchase_price = float(mean_purchase['mean_purchase_price'])
                        logger.debug("mean_purchase_price from db:{}".format(mean_purchase_price))
                        if mean_purchase_prices != 0:
                            mean_purchase_prices.append(mean_purchase_price)
                        else:
                            logger.debug(" zero mean_purchase_price from db:{}".format(mean_purchase_price))
                            continue
          
                 possible_open_order = True
                 _trader.try_to_sell_UNSOLD(semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,last_candle_df.iloc[0]['rsi'],output_rsi,quote_balance,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,model['sos_rate'],mean_purchase_prices) 
                #it's dangerous, do it manually in beta. 
                # _trader.try_to_sell_NOW(semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,quote_balance) 
                 continue

        if base_balance < model['sos_amount'] and enought_quote_balance:
             logger.debug("base_balance less than sos_amount:{} SOS!!".format(model['sos_amount']))
             possible_open_order = True
             if send_state:
                _matrix.send("State trying to sell SOS {0} . Base_balance {1} less than sos_amount:{2} SOS!!".format(currency_pair,base_balance,model['sos_amount'])) 
             _trader.try_to_sell_SOS(semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,last_candle_df.iloc[0]['rsi'],output_rsi,quote_balance,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,model['sos_rate'],mean_purchase_prices) 
             continue

        #rsi mode always 1 so never buy if rsi is high 
        if rsi_mode:  
            if last_candle_df.iloc[0]['rsi'] >  (output_rsi / 1000.0):
                logger.debug("rsi output reached:{}".format(last_candle_df.iloc[0]['rsi']))
                logger.debug("good point to sell...")
                available_balances = _poloniex.get_available_balances(semaphore,logger)
                if available_balances == False:
                    logger.debug("Error getting available_balances:{}".format(available_balances))
                    continue
                base_balance = float(available_balances[base_currency])
                quote_balance = float(available_balances[quote_currency])
                enought_quote_balance = False
                if amount_invested_in_base > 2.0:
                    enought_quote_balance = True
                logger.debug("enought_quote_balance:{}".format(enought_quote_balance)) 

                if enought_quote_balance:
                    possible_open_order = True
                    _trader.try_to_sell (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,quote_balance,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,mean_purchase_prices)
            else:
                if model['func']  == 0:
                    if  _invest.shouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                        available_balances = _poloniex.get_available_balances(semaphore,logger)
                        if available_balances == False:
                            logger.debug("Error getting available_balances:{}".format(available_balances))
                            continue
                        base_balance = float(available_balances[base_currency])
                        quote_balance = float(available_balances[quote_currency])
                        if base_balance > model['initial_amount_to_buy_in_base'] :
                            possible_open_order = True
                            logger.debug("free_to_buy:{}".format(free_to_buy))
                            if free_to_buy:
                                logger.debug("calling try_to_buy_in_base...") 
                                _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                        else:
                            logger.debug("Insuficcient base balance:{}".format(base_balance))
                if model['func']  == 1:
                    if  _invest.simpleDownShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                        
                        available_balances = _poloniex.get_available_balances(semaphore,logger)
                        if available_balances == False:
                            logger.debug("Error getting available_balances:{}".format(available_balances))
                            continue
                        base_balance = float(available_balances[base_currency])
                        quote_balance = float(available_balances[quote_currency])

                        if base_balance > model['initial_amount_to_buy_in_base'] :
                            possible_open_order = True
                            logger.debug("free_to_buy:{}".format(free_to_buy))
                            if free_to_buy:
                                logger.debug("calling try_to_buy_in_base...") 
                                _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                        else:
                            logger.debug("Insuficcient base balance:{}".format(base_balance))
                if model['func']  == 2:
                    if  _invest.simpleShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                        available_balances = _poloniex.get_available_balances(semaphore,logger)
                        if available_balances == False:
                            logger.debug("Error getting available_balances:{}".format(available_balances))
                            continue
                        base_balance = float(available_balances[base_currency])
                        quote_balance = float(available_balances[quote_currency])
                        if base_balance > model['initial_amount_to_buy_in_base'] :
                            possible_open_order = True
                            logger.debug("free_to_buy:{}".format(free_to_buy))
                            if free_to_buy:
                                logger.debug("calling try_to_buy_in_base...") 
                                _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                        else:
                            logger.debug("Insuficcient base balance:{}".format(base_balance))
        else:
           #rsi_mode is 0, so it is possible buy with high rsi. 
            if model['func']  == 0:
                if  _invest.shouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                    available_balances = _poloniex.get_available_balances(semaphore,logger)
                    if available_balances == False:
                        logger.debug("Error getting available_balances:{}".format(available_balances))
                        continue
                    base_balance = float(available_balances[base_currency])
                    quote_balance = float(available_balances[quote_currency])
                    if base_balance > model['initial_amount_to_buy_in_base'] :
                        possible_open_order = True
                        logger.debug("free_to_buy:{}".format(free_to_buy))
                        if free_to_buy:
                            logger.debug("calling try_to_buy_in_base...") 
                            _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                            continue
                    else:
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
            if model['func']  == 1:
                if  _invest.simpleDownShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                    
                    available_balances = _poloniex.get_available_balances(semaphore,logger)
                    if available_balances == False:
                        logger.debug("Error getting available_balances:{}".format(available_balances))
                        continue
                    base_balance = float(available_balances[base_currency])
                    quote_balance = float(available_balances[quote_currency])

                    if base_balance > model['initial_amount_to_buy_in_base'] :
                        possible_open_order = True
                        logger.debug("free_to_buy:{}".format(free_to_buy))
                        if free_to_buy:
                            logger.debug("calling try_to_buy_in_base...") 
                            _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                            continue
                    else:
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
            if model['func']  == 2:
                if  _invest.simpleShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair,remote_data_base_config):
                    available_balances = _poloniex.get_available_balances(semaphore,logger)
                    if available_balances == False:
                        logger.debug("Error getting available_balances:{}".format(available_balances))
                        continue
                    base_balance = float(available_balances[base_currency])
                    quote_balance = float(available_balances[quote_currency])
                    if base_balance > model['initial_amount_to_buy_in_base'] :
                        possible_open_order = True
                        logger.debug("free_to_buy:{}".format(free_to_buy))
                        if free_to_buy:
                            logger.debug("calling try_to_buy_in_base...") 
                            _trader.try_to_buy_in_base (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,mean_purchase_prices,global_quote_percent.value)
                            continue
                    else:
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
           #if not buy maybe sell
            if last_candle_df.iloc[0]['rsi'] >  (output_rsi / 1000.0):
                logger.debug("rsi output reached:{}".format(last_candle_df.iloc[0]['rsi']))
                logger.debug("good point to sell...")
                available_balances = _poloniex.get_available_balances(semaphore,logger)
                if available_balances == False:
                    logger.debug("Error getting available_balances:{}".format(available_balances))
                    continue
                base_balance = float(available_balances[base_currency])
                quote_balance = float(available_balances[quote_currency])
                enought_quote_balance = False
                if amount_invested_in_base > 2.0:
                    enought_quote_balance = True
                logger.debug("enought_quote_balance:{}".format(enought_quote_balance)) 

                if enought_quote_balance:
                    possible_open_order = True
                    _trader.try_to_sell (semaphore,logger,remote_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,quote_balance,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,mean_purchase_prices)
                    continue


            
if __name__ == "__main__":

    from models_data import models
    time.sleep(300)
   
    processes = []
    semaphore = multiprocessing.Semaphore()
    global_quote_percent = multiprocessing.Value('d',0.0)
    exits_BTC = False #BTC is the leading currency that must always exist to synchronize the process
    for model in models:
        if model['currency_pair'] == "USDC_BTC":
            exits_BTC = True

    if exits_BTC:
        for model in models:
            process = multiprocessing.Process(target = main, args=(semaphore,model,global_quote_percent))
            time.sleep(random.randint(1, 10))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()    

