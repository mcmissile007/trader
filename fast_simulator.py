from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
#import matplotlib.pyplot as plt
#from scipy.signal import argrelextrema
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import pymysql
import sys
import os
import glob
import requests
import urllib
import hmac
import multiprocessing
import random
import math


from database_config import local_data_base_config
from learning_funcs import calculate_learning_dataframe_from_db

import invest_funcs as _invest
import database_funcs as _db
import models_funcs as _md_funcs
import math_funcs as _mth
import simulator_funcs as _sim


def main(logger, models_testing):

  
    
    time_frame = 300
    day_before_learning = 100
    while (True):
        model = _md_funcs.getModeltoTest()
        if  model['hash'] in models_testing:
            continue
        if  _db.existResult(logger,local_data_base_config,model['hash']):
            continue
        break
    models_testing.append(model['hash'])
  

    currency_pair = model['currency_pair']
    always_win = model['always_win'] 
    min_current_rate_benefit = model['min_current_rate_benefit'] 
    max_amount_to_buy_in_base = model['max_amount_to_buy_in_base']
    initial_amount_to_buy_in_base = model['initial_amount_to_buy_in_base'] 
    currencies = currency_pair.split("_") 
    base_currency = currencies[0]
    quote_currency = currencies[1] 
    output_rsi = int(model['ben_field'].split('_')[1])   

    start_time_simulation = 1559692800 #    Wednesday, June 5, 2019 0:00:00 BTC 7680
    end_time_simulation = 1574985600 #  Friday, November 29, 2019 0:00:00 BTC 7736 
    step = 0
     
    now = start_time_simulation - time_frame
    reload_learning_dataframe_interval = 86400 
    days_before = 100
    base_balance = []
    quote_balance = []
    purchase_operations =[]
    trade_operations = []
    repurchases = []
    games =  []
    sos_games = []
    base_balance.append(6000)
    quote_balance.append(0)
    time_start_sim = int(time.time())
    file_name_pkl = "tickets_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + ".pkl"
    if os.path.exists("data/" + file_name_pkl):
        tickets_df = pd.read_pickle("data/" + file_name_pkl)
    else:
        logger.error(f"Error reading tickets dataframe:no file data")
        return
    if tickets_df.empty:
        logger.error(f"Error reading tickets dataframe,empty dataframe")
        return

    file_name_pkl = "candles_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + "_"  + str(time_frame)  +".pkl"
    if os.path.exists("data/" + file_name_pkl):
        full_candles_df = pd.read_pickle("data/" + file_name_pkl)
    else:
        logger.error(f"Error reading candles dataframe:no file data")
        return
    if full_candles_df.empty:
        logger.error(f"Error reading candles dataframe,empty dataframe")
        return
    
    
    while (True):
        step += 1
        now += time_frame
        if now > end_time_simulation:
           break
        time_working_with_same_learning_dataframe = step * time_frame
        if now == start_time_simulation or time_working_with_same_learning_dataframe > reload_learning_dataframe_interval:
            step = 0
            file_name_pkl = str(now) + "_"  + str(days_before) + "_" + currency_pair + "_" + str(time_frame) + ".pkl"
            if os.path.exists("data/" + file_name_pkl):
                learning_df = pd.read_pickle("data/" + file_name_pkl)
            else:
                learning_df = calculate_learning_dataframe_from_db(logger,local_data_base_config,time_frame,currency_pair,output_rsi,now,days_before)
                if not learning_df.empty:               
                    learning_df.to_pickle("data/" + file_name_pkl )
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

        max_num_of_results = 300
      
        candles_df = full_candles_df[(full_candles_df.date < (now)) & (full_candles_df.date >= (now-(max_num_of_results*time_frame)) )].copy(deep = True)
        
        

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
        delay = 10
        ticket = tickets_df[tickets_df.epoch < (now+delay)].tail(1)
        if ticket.empty:
            logger.info("Error getting last ticket to calculate amount_invested:{}".format(ticket))
            return
     
        last = float(ticket.iloc[0]['last'])
        highestBid = float(ticket.iloc[0]['highestBid'])
        lowestAsk = float(ticket.iloc[0]['lowestAsk'])
       
        amount_invested_in_base  = sum(quote_balance) * last
        logger.debug("amount_invested in base for current rate:{}".format(amount_invested_in_base))
        logger.debug("amount to sell in quote currency:{}".format(sum(quote_balance)))
        enought_quote_balance = False
       


        if amount_invested_in_base > 1.0:
            enought_quote_balance = True
        logger.debug("enought_quote_balance:{}".format(enought_quote_balance)) 
        if sum(base_balance) < float(model['amount_to_sos_mode'])  and enought_quote_balance:
             logger.debug("base_balance less than max_amount_to_buy_in_base:{} SOS!!".format(sum(base_balance)))
             sos_model_benefit = float(model['sos_model_benefit'])
             _sim.sim_sell_SOS(logger,local_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,purchase_operations,trade_operations,quote_balance,now,sos_model_benefit,sos_games,last,highestBid) 
             continue

        #rsi mode always 1 so never buy if rsi is high 
        if last_candle_df.iloc[0]['rsi'] >  (output_rsi / 1000.0):
            logger.debug("rsi output reached:{}".format(last_candle_df.iloc[0]['rsi']))
            logger.debug("good point to sell...")
            if len(purchase_operations) > 0  and  enought_quote_balance:
                logger.debug("rsi output reached:{}".format(last_candle_df.iloc[0]['rsi']))
                logger.debug("good point to sell...")
                _sim.sim_sell (logger,local_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,purchase_operations,trade_operations,quote_balance,now,games,last,highestBid)
            else:
                pass
                logger.debug("none purchase operations or not enought_quote_balance ")
        else:
            if model['func']  == 0:
                if  _invest.shouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair):
                    if sum(base_balance) > model['initial_amount_to_buy_in_base']:
                        _sim.sim_buy_in_base (logger,local_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,purchase_operations,trade_operations,base_balance,quote_balance,now,repurchases,last,lowestAsk)
                    else:
                        pass
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
            if model['func']  == 1:
                if  _invest.simpleDownShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair):
                    if sum(base_balance) > model['initial_amount_to_buy_in_base'] :
                        _sim.sim_buy_in_base (logger,local_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,purchase_operations,trade_operations,base_balance,quote_balance,now,repurchases,last,lowestAsk)
                    else:
                        pass
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
            if model['func']  == 2:
                if  _invest.simpleShouldIInvest(logger,learning_df,last_candle_df,model,now,currency_pair):
                    if sum(base_balance) > model['initial_amount_to_buy_in_base'] :
                        _sim.sim_buy_in_base (logger,local_data_base_config,currency_pair,last_candle_df.iloc[0]['close'],last_candle_df.iloc[0]['roc1'],time_frame,output_rsi,model,purchase_operations,trade_operations,base_balance,quote_balance,now,repurchases,last,lowestAsk)
                    else:
                        pass
                        logger.debug("Insuficcient base balance:{}".format(base_balance))
    
    
    time_end_sim = int(time.time())
    time_sim_in_seconds = time_end_sim - time_start_sim
    logger.info("time_sim_in_seconds:{}".format(time_sim_in_seconds))
    
    max_inversion = max(trade_operations,key=lambda x:x[0])[0]
    logger.info("max_inversion:{}".format(max_inversion))
    mean_inversion = np.mean([ x[0] for x in trade_operations ])
    logger.info("mean_inversion:{}".format(mean_inversion))
    median_inversion = np.median([ x[0] for x in trade_operations ])
    logger.info("median_inversion:{}".format(median_inversion))
   
    max_benefit = max(trade_operations,key=lambda x:x[1])[1]
    logger.info("max_benefit:{}".format(max_benefit))
    mean_benefit= np.mean([ x[1] for x in trade_operations ])
    logger.info("mean_benefit:{}".format(mean_benefit))

    total_benefit = sum( [ x[1] for x in trade_operations ] )
    logger.info("total_benefit:{}".format(total_benefit))

    max_benefit_rate = max(trade_operations,key=lambda x:x[2])[2]
    logger.info("max_benefit_rate:{}".format(max_benefit_rate))
    mean_benefit_rate= np.mean([ x[2] for x in trade_operations ])
    logger.info("mean_benefit_rate:{}".format(mean_benefit_rate))

    total_repurchases = sum(repurchases)
    total_purchases = float(len(repurchases))
    total_games = float(len(games))
    total_sos_games = float(len(sos_games))
    if total_purchases > 0:
        repurchase_rate =  (total_repurchases / total_purchases)
    else:
        repurchase_rate = 0.0

    if total_games > 0:
        result_sos_rate = total_sos_games/total_games
    else:
        result_sos_rate = 0.0
    
    code_repurchases  =  []
    count = 0
    for value in repurchases:
        if value == 0 :
            if count > 0:
                code_repurchases.append(count)
                code_repurchases.append(0)
                count = 0
            else:
                code_repurchases.append(0)
        else:
            count += 1
    if count > 0:
        code_repurchases.append(count)

    
    median_repurchases = np.median(code_repurchases)
    mean_repurchases =  np.mean(code_repurchases)
    max_repurchases = max(code_repurchases)
   
    logger.info("total_games:{}".format(total_games))
    logger.info("total_sos_games:{}".format(total_sos_games))
    logger.info("result_sos_rate:{}".format(result_sos_rate))
    
    logger.info("num_purchases:{}".format(total_purchases))
    logger.info("num_repurchases:{}".format(total_repurchases))
    logger.info("repurchase_rate:{}".format(repurchase_rate))
    logger.info("median_repurchases:{}".format(median_repurchases))
    logger.info("mean_repurchases:{}".format(mean_repurchases))
    logger.info("max_repurchases:{}".format(max_repurchases))

 
    logger.info("sum base_balance:{}".format(sum(base_balance)))
    logger.info("sum quote_balance:{}".format(sum(quote_balance))) 

    data_for_log = {}
    data_for_log['m_hash'] = model['hash']
    data_for_log['m_currency_pair'] = model['currency_pair']
    data_for_log['m_always_win'] = int(model['always_win'] == True)
    data_for_log['m_min_rate'] = model['min_current_rate_benefit']
    data_for_log['m_init_amount'] = model['initial_amount_to_buy_in_base']
    data_for_log['m_max_amount'] = model['max_amount_to_buy_in_base']
    data_for_log['m_min_amount'] = model['min_amount_to_buy_in_base']
    data_for_log['m_sos_amount'] = model['amount_to_sos_mode']
    data_for_log['m_sos_rate'] = model['sos_model_benefit']
    data_for_log['m_mode'] = model['mode']
    data_for_log['m_func'] = model['func']
    data_for_log['m_avg'] = model['avg']
    data_for_log['m_r'] = model['r']
    data_for_log['m_min_roc1'] = model['min_roc1']
    data_for_log['m_max_roc1'] = model['max_roc1']

    
    data_for_log['r_time_sim'] = time_sim_in_seconds
    data_for_log['r_total_benefit'] = total_benefit
    data_for_log['r_max_benefit'] = max_benefit
    data_for_log['r_mean_benefit'] = mean_benefit
    data_for_log['r_max_benefit_rate'] = max_benefit_rate
    data_for_log['r_mean_benefit_rate'] = mean_benefit_rate
    data_for_log['r_max_inversion'] = max_inversion
    data_for_log['r_mean_inversion'] = mean_inversion
    data_for_log['r_median_inversion'] = median_inversion
    data_for_log['r_num_purchases'] = total_purchases
    data_for_log['r_num_repurchases'] = total_repurchases
    data_for_log['r_repurchase_rate'] = repurchase_rate
    data_for_log['r_median_repurchases'] = median_repurchases
    data_for_log['r_max_repurchases'] = max_repurchases
    data_for_log['r_num_games'] = total_games
    data_for_log['r_num_sos_games'] = total_sos_games
    data_for_log['r_sos_rate'] = result_sos_rate

    data_for_log['r_base_balance'] = sum(base_balance)
    data_for_log['r_quote_balance'] = sum(quote_balance)

    #_db.logInsertResult(logger,local_data_base_config,data_for_log)
    _db.insert(logger,local_data_base_config,"results",data_for_log)
    

def main_test(cpu,models_testing):
    time.sleep(random.choice([1,3,2]))
    if not cpu in models_testing:
        models_testing.append(cpu)

    return

if __name__ == "__main__":


    processes = []
    loggers = [] 
    models_testing = multiprocessing.Manager().list()

   
  
    number_of_cpus = multiprocessing.cpu_count()
    #number_of_cpus = 2
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("fast_simulating")
    log_file_name = "fast_simulating"
    filename =  "./logs/" + log_file_name + "_" + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    loggers.append(logger)

    for cpu in range(number_of_cpus):
        process = multiprocessing.Process(target = main, args=(logger,models_testing))
        process.start()
        processes.append(process)
        
        
    while (True):  
        
        processes_to_remove =  []
        time.sleep(10)
        for process_item in processes:
            if process_item.is_alive() == False:
                processes_to_remove.append(process_item)
               
        for process_to_remove in processes_to_remove:
            processes.remove(process_to_remove)
            process = multiprocessing.Process(target = main, args=(logger,models_testing))
            process.start()
            processes.append(process)
