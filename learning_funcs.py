from datetime import datetime, timedelta
import time
import pandas as pd
import database_funcs as _db
import math_funcs as _mth

def get_candles_from_db(logger,rd,data_base_config,currency_pair):
    
    if rd['time_frame'] not in [300,900,1800,7200,14400,86400]:
        logger.error ("Invalid time_frame")
        return False
    try:
        from_time = int(datetime(rd['from_date']['year'],rd['from_date']['month'],rd['from_date']['day'],0,0).timestamp())
        to_time = int(datetime(rd['to_date']['year'],rd['to_date']['month'],rd['to_date']['day'],0,0).timestamp())
    except Exception as e:
        logger.error(e)
        return False
    if to_time <= from_time:
        logger.error("Invalid dates")
        return False

    return  _db.getCandlesFromTickets(logger,data_base_config,currency_pair,rd['time_frame'],from_time,to_time)



def validate_candles_from_db(logger,data_frame,time_frame):
    if not "date" in data_frame.columns:
        logger.error("Not date in data frame")
        return False
    if not "close" in data_frame.columns:
        logger.error("Not close in data frame")
        return False
    if not "open" in data_frame.columns:
        logger.error("Not open in data frame")
        return False
    date_series = pd.Series(data_frame['date'])
    if True in date_series.isnull().values:
        logger.error("Nan values in date serie")
        return False
    if  (data_frame['close'] == 0).any():
        logger.error("close_series 0")
        return False

    if (data_frame['open'] == 0).any():
        logger.error("open_series 0")
        return False
    return True



def simulate(df,rsi_th):
    i = 0
    benefits = []
    steps =[]
    indexes_out =[]  
    while i <= df.index[-1]:
        benefit = 0
        for j in range(100000):
            if i + j == df.index[-1]:
                benefit = (df.loc[i+j,'close']/df.loc[i,'close']) - 1.0
                break
            if j == 0:
                continue
            rsi = df.loc[i+j,'rsi']
            if rsi > rsi_th :
                benefit = (df.loc[i+j,'close']/df.loc[i,'close']) - 1.0
                break
        steps.append(j)
        indexes_out.append(i+j)
        benefits.append(benefit)
        i += 1
    return (pd.Series(benefits),pd.Series(steps),pd.Series(indexes_out),) 


def calculate_learning_dataframe_from_db(logger,remote_data_base_config,time_frame,currency_pair,output_rsi):
    retries = 3
    data_ok = False
    while (retries > 0):
        time.sleep(5)
        retries -= 1
        end_date = datetime.now() - timedelta(days=1) 
        start_date = end_date - timedelta(days=100)
        from_date = {'year':start_date.year,'month':start_date.month,'day':start_date.day} 
        to_date = {'year':end_date.year,'month':end_date.month,'day':end_date.day} 
        request_data ={'currency_pair' : currency_pair, 'time_frame': time_frame, 'from_date': from_date, 'to_date': to_date}
        logger.debug("request_data{}".format(request_data))
        data = get_candles_from_db(logger,request_data,remote_data_base_config,currency_pair) #data is sorted by epoch
        if data is not False:
            candles_df =  pd.DataFrame(data,columns=['date','open','low','high','close'])
            if candles_df.empty :
                time.sleep(10)
                logger.debug("candles_df empty. Try again...")
                continue
            candles_df    
            candles_df['diff'] =  abs(candles_df["date"].diff())
            logger.debug(candles_df.head())
            logger.debug(candles_df.tail())
            candles_df = candles_df.reset_index(drop=True) 
            logger.debug(candles_df.head())
            logger.debug(candles_df.tail())
            candles_df = candles_df[candles_df['diff']  == request_data['time_frame']]
            logger.debug(candles_df.head())
            logger.debug(candles_df.tail())
            candles_df = candles_df.reset_index(drop=True)#important to make future calculus with index 
            if candles_df.empty :
                time.sleep(10)
                logger.debug("candles_df empty after filter. Try again...")
                continue 
            
            if not  validate_candles_from_db(logger,candles_df,request_data['time_frame']):
                time.sleep(10)
                logger.debug("Not validate_candles_from_poloniex. Try again...")
                continue

            data_ok = True
            break
            
        else:
            time.sleep(10)
            logger.debug("Error getting candles . Try again...")
            continue 
    if  data_ok == False :
        return pd.DataFrame()
        

    logger.debug("Candles OK")
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
    sma50_delta_mean = candles_df.sma50_delta.mean()
    sma50_delta_std = candles_df.sma50_delta.std()
    candles_df['sma50_delta_z'] = (candles_df.sma50_delta - sma50_delta_mean)/sma50_delta_std
    
    candles_df['ema26_delta'] = (candles_df.close - candles_df.ema26)/candles_df.ema26
    ema26_delta_mean = candles_df.ema26_delta.mean()
    ema26_delta_std = candles_df.ema26_delta.std()
    candles_df['ema26_delta_z'] = (candles_df.ema26_delta - ema26_delta_mean)/ema26_delta_std
    
    candles_df['ema13_delta'] = (candles_df.close - candles_df.ema13)/candles_df.ema13
    ema13_delta_mean = candles_df.ema13_delta.mean()
    ema13_delta_std = candles_df.ema13_delta.std()
    candles_df['ema13_delta_z'] = (candles_df.ema13_delta -ema13_delta_mean )/ema13_delta_std
    
    
    roc0_mean = candles_df.roc0.mean()
    roc0_std = candles_df.roc0.std()
    candles_df['roc0_z'] = (candles_df.roc0 - roc0_mean)/roc0_std
    
    roc1_mean = candles_df.roc1.mean()
    roc1_std = candles_df.roc1.std()
    candles_df['roc1_z'] = (candles_df.roc1 - roc1_mean)/roc1_std

    roc3_mean = candles_df.roc3.mean()
    roc3_std = candles_df.roc3.std()
    candles_df['roc3_z'] = (candles_df.roc3 - roc3_mean)/roc3_std

    roc6_mean = candles_df.roc6.mean()
    roc6_std = candles_df.roc6.std()
    candles_df['roc6_z'] = (candles_df.roc6 - roc6_mean)/roc6_std

    roc12_mean = candles_df.roc12.mean()
    roc12_std = candles_df.roc12.std()
    candles_df['roc12_z'] = (candles_df.roc12 - roc12_mean)/roc12_std

    roc24_mean = candles_df.roc24.mean()
    roc24_std = candles_df.roc24.std()
    candles_df['roc24_z'] = (candles_df.roc24 - roc24_mean)/roc24_std

    roc48_mean = candles_df.roc48.mean()
    roc48_std = candles_df.roc48.std()
    candles_df['roc48_z'] = (candles_df.roc48 - roc48_mean)/roc48_std

    roc72_mean = candles_df.roc72.mean()
    roc72_std = candles_df.roc72.std()
    candles_df['roc72_z'] = (candles_df.roc72 - roc72_mean)/roc72_std

    roc288_mean = candles_df.roc288.mean()
    roc288_std = candles_df.roc288.std()
    candles_df['roc288_z'] = (candles_df.roc288 - roc288_mean)/roc288_std
    
    
    trix_mean = candles_df.trix.mean()
    trix_std = candles_df.trix.std()
    candles_df['trix_z'] = (candles_df.trix - trix_mean)/trix_std
    

    rsi_mean = candles_df.rsi.mean()
    rsi_std = candles_df.rsi.std()
    candles_df['rsi_z'] = (candles_df.rsi - rsi_mean)/rsi_std


    macd_mean = candles_df.macd.mean()
    macd_std = candles_df.macd.std()
    candles_df['macd_z'] = (candles_df.macd - macd_mean)/macd_std


    histogram_mean = candles_df.histogram.mean()
    histogram_std = candles_df.histogram.std()
    candles_df['histogram_z'] = (candles_df.histogram - histogram_mean)/histogram_std

    rsi = output_rsi 
    benefit_name = "b_" + str(rsi) 
    steps_name = "step_" + str(rsi)
    indexes_out_name = "iout_" + str(rsi)
    start = int(time.time())
    benefits,steps,indexes_out = simulate(candles_df,(rsi/1000.0))
    candles_df[benefit_name] = benefits 
    candles_df[steps_name] = steps
    candles_df[indexes_out_name] = indexes_out 
    end = int(time.time())
    diff_time = (end - start)/60
    return candles_df[288:].copy(deep = True) 