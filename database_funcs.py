
import time
from datetime import datetime
import pymysql
from currency_codes import codes

def insert(logger,data_base_config,table_name, m_dict):
    #tested with results

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                                        user=data_base_config['user'],
                                        password=data_base_config['password'],
                                        db=data_base_config['db'],
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        logger.error("Error data base connection: %s", str(e))
        return False

    sql = "insert into " + table_name + " ("
    for key in m_dict:
        sql += key + ","
    sql = sql[:-1]
    sql += ") values("
    for key in m_dict:
        if type(m_dict[key]) == str:
            sql += "'" + m_dict[key] + "',"
        else:
            sql += str(m_dict[key]) + ","
    sql = sql[:-1]
    sql += ")"
    logger.debug(sql)
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
    except pymysql.OperationalError as error:
        logger.error("OperationalError data base: %s", str(error))
        logger.error("sql:%s", sql)
        return False
    except Exception as e:
        logger.error("Error data base: %s", str(e))
        logger.error("sql:%s", sql)
        return False
    return True

def getBalanceFromDB(logger, data_base_config, now):
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                                        user=data_base_config['user'],
                                        password=data_base_config['password'],
                                        db=data_base_config['db'],
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        logger.error("Error data base connection: %s", str(e))
        return False

    sql = "select epoch,currency,amount,percent from log_balances where "
    sql += " epoch = " + str(now)
    try:

        with db_connection.cursor() as cursor:
            logger.debug("%s", sql)
            cursor.execute(sql)
            results = list(cursor.fetchall())
            logger.debug("%s", results)
            if len(results) > 0:
                return results
            else:
                logger.debug("no results")
                return False

    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False


def getCandlesFromTickets(logger,data_base_config,currency_pair,time_frame,start,end):

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

    offset = 16
    if time_frame == 300: 
        offset = 288
    if time_frame == 900: 
        offset = 96
    if time_frame == 1800: 
        offset = 32

    start_th = start - ((offset)*time_frame)
 
    sql = "select epoch,last from tickets  where " 
    sql += " currency_pair='" + currency_pair  + "'"
    sql += " and epoch >=" + str(start_th) + " and epoch <=" + str(end)
    sql += " order by epoch asc" 
    results= [] 
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("sql:{}".format(sql))
            cursor.execute(sql)
            results = list(cursor.fetchall())
            if len(results) < 1:
                logger.debug("No results!")
                return False

    except Exception as e:
        logger.error("sql:{} exception:{} ".format(sql,e))
        return False

    buffer_candles = [] 
    for value_start in range (start,end,time_frame):
        new_candle = {} 
        b_start = value_start
        b_end = value_start + time_frame
        candle_values =[] 
        for i,item in enumerate(results):
            item_epoch = item['epoch']
            item_last = item['last']
            if candle_values == [] and item_epoch > b_start:
                if (i-1) > 0:
                    candle_values.append(results[i-1]['last'])
                else: 
                    candle_values.append(item_last)
                continue
            if candle_values != []   and item_epoch <= b_end:
                candle_values.append(item_last)
                continue
            if item_epoch > b_end:
                break
        if len(candle_values) > 0:
            open_value = candle_values[0]
            close_value = candle_values[-1] 
            lower_value = min(candle_values) 
            upper_value = max(candle_values)
            new_candle['date'] = b_start
            new_candle['ts'] = datetime.utcfromtimestamp(b_start)
            new_candle['open'] = open_value
            new_candle['low'] =  lower_value
            new_candle['high'] =  upper_value
            new_candle['close'] =  close_value
            buffer_candles.append(new_candle)
            continue
        else:
            if len(buffer_candles) == 0:
                logger.error("Error not initial candle")
                return False
            last_candle = buffer_candles[-1]
            new_candle['date'] = b_start
            new_candle['ts'] = datetime.utcfromtimestamp(b_start)
            new_candle['open'] =  last_candle['close']  
            new_candle['low'] =   last_candle['close'] 
            new_candle['high'] =   last_candle['close'] 
            new_candle['close'] =   last_candle['close']
            buffer_candles.append(new_candle)  
            continue
    initial_value = buffer_candles[0]['close']  
    for i,candle in enumerate(buffer_candles):#index of the first diferent candle, real candle 
        if candle['close'] != initial_value:
            break
  
    return buffer_candles[i:] 


def existResult(logger,data_base_config,hash_code):

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

   
    sql = "select m_hash from results where " 
    sql += " m_hash='" + hash_code + "'"
    
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("%s",sql)
            cursor.execute(sql)
            results = list(cursor.fetchall())
            if len(results) > 0:
                return True 
            else:
                logger.debug("no results")
                return False
       
    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False

def getLastCandlesFromTickets(logger, data_base_config, currency_pair, time_frame, now, max_num_of_results):
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                                        user=data_base_config['user'],
                                        password=data_base_config['password'],
                                        db=data_base_config['db'],
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        logger.error("Error data base connection: %s", str(e))
        return False
    end = now
    offset = 16
    if time_frame == 300:
        offset = 288
    if time_frame == 900:
        offset = 96
    if time_frame == 1800:
        offset = 32
    start = now - ((max_num_of_results+offset)*time_frame)
    sql = "select epoch,last from tickets  where "
    sql += " currency_pair='" + currency_pair + "'"
    sql += " and epoch >=" + str(start) + " and epoch <=" + str(end)
    sql += " order by epoch asc"
    results = []
    try:
        with db_connection.cursor() as cursor:
            logger.debug("sql:{}".format(sql))
            cursor.execute(sql)
            results = list(cursor.fetchall())
            #print(results)
            if len(results) < 1:
                logger.debug("No results!")
                return False

    except Exception as e:
        logger.debug("sql:{} exception:{} ".format(sql, e))
        return False
    global_end = now
    gobal_start = now - (max_num_of_results*time_frame)
    buffer_candles = []
    for value_start in range(gobal_start, global_end, time_frame):
        new_candle = {}
        b_start = value_start
        b_end = value_start + time_frame
        candle_values = []
        for i, item in enumerate(results):
            item_epoch = item['epoch']
            item_last = item['last']

            
            
            if candle_values == [] and item_epoch < b_start:
                continue
           
            if candle_values == [] and item_epoch == b_start:
                candle_values.append(item_last)
                continue
            if candle_values == [] and item_epoch > b_start: 
                if (i-1) > 0:
                    candle_values.append(results[i-1]['last']) #insert the last close as first, no jumps
                candle_values.append(item_last)
                continue
        
            if candle_values != [] and item_epoch <= b_end:
                candle_values.append(item_last)
                continue

            if item_epoch > b_end:
                break
            

        if len(candle_values) > 0:
            open_value = candle_values[0]
            close_value = candle_values[-1]
            lower_value = min(candle_values)
            upper_value = max(candle_values)
            new_candle['date'] = b_start
            new_candle['ts'] = datetime.utcfromtimestamp(b_start)
            new_candle['open'] = open_value
            new_candle['low'] = lower_value
            new_candle['high'] = upper_value
            new_candle['close'] = close_value
            buffer_candles.append(new_candle)
            continue
        else:
            if len(buffer_candles) == 0:
                logger.error("Error not initial candle")
                return False
            last_candle = buffer_candles[-1]
            new_candle['date'] = b_start
            new_candle['ts'] = datetime.utcfromtimestamp(b_start)
            new_candle['open'] = last_candle['close']
            new_candle['low'] = last_candle['close']
            new_candle['high'] = last_candle['close']
            new_candle['close'] = last_candle['close']
            buffer_candles.append(new_candle)
            continue

    return buffer_candles



def logInsertResult(logger,data_base_config,data):

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False
                             
    sql = "insert into results(m_hash,m_currency_pair,m_always_win,m_min_rate,m_init_amount,m_max_amount,m_min_amount,m_sos_amount,m_sos_rate,m_mode,m_func,m_avg,m_r,m_min_roc1,m_max_roc1,"
    sql += "r_time_sim,r_total_benefit,r_max_benefit,r_mean_benefit,r_max_benefit_rate,r_mean_benefit_rate,r_max_inversion,r_mean_inversion,r_median_inversion,r_num_purchases,r_num_repurchases," 
    sql += "r_repurchase_rate,r_median_repurchases,r_max_repurchases,r_num_games,r_num_sos_games,r_sos_rate,r_base_balance,r_quote_balance) values(" 
    sql +=  "'" + str(data['m_hash'] ) + "','"
    sql += str(data['m_currency_pair'] ) + "',"
    sql += str(data['m_always_win']) + ","
    sql += str(data['m_min_rate']) + ","
    sql += str(data['m_init_amount']) + ","
    sql += str(data['m_max_amount']) + ","
    sql += str(data['m_min_amount']) + ","
    sql += str(data['m_sos_amount']) + ","
    sql += str(data['m_sos_rate']) + ","
    sql += str(data['m_mode']) + ","
    sql += str(data['m_func']) + ","
    sql += str(data['m_avg']) + ","
    sql += str(data['m_r']) + ","
    sql += str(data['m_min_roc1']) + ","
    sql += str(data['m_max_roc1']) + ","
    sql += str(data['r_time_sim']) + ","
    sql += str(data['r_total_benefit']) + ","
    sql += str(data['r_max_benefit']) + ","
    sql += str(data['r_mean_benefit']) + ","
    sql += str(data['r_max_benefit_rate']) + ","
    sql += str(data['r_mean_benefit_rate']) + ","
    sql += str(data['r_max_inversion']) + ","
    sql += str(data['r_mean_inversion']) + ","
    sql += str(data['r_median_inversion']) + ","
    sql += str(data['r_num_purchases']) + ","
    sql += str(data['r_num_repurchases']) + ","
    sql += str(data['r_repurchase_rate']) + ","
    sql += str(data['r_median_repurchases']) + ","
    sql += str(data['r_max_repurchases']) + ","
    sql += str(data['r_num_games']) + ","
    sql += str(data['r_num_sos_games']) + ","
    sql += str(data['r_sos_rate']) + ","
    sql += str(data['r_base_balance']) + ","
    sql += str(data['r_quote_balance']) + ")"
    logger.debug("sql:{}".format(sql))
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
        
    except Exception as e:
        logger.error("Error data base: %s",str(e))
        logger.error("sql:%s",sql) 
        return False  
    return True



def logInsertCancelOrder(logger,data_base_config,currency_pair,_type,model_name,model_key,orderNumber,response):
    _type="cancel_" + _type
    model = model_name
    price = 0.0
    amount_in_quote = 0.0
    amount_in_base = 0.0
    increment = 0.0
    last = 0.0
    highestBid = 0.0
    lowestAsk = 0.0
    output_rsi = 0.5
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False
                             
    sql = "insert into log_orders(epoch,currency_pair,type,price,amount_in_quote,amount_in_base,model,increment,model_key,last,highestBid,lowestAsk,output_rsi,orderNumber,response) values(" 
    sql += str(int(time.time())) + ",'"
    sql += currency_pair + "','"
    sql += _type + "',"
    sql += str(price) + ","
    sql += str(amount_in_quote) + ","
    sql += str(amount_in_base) + ",'"
    sql += model + "',"
    sql += str(increment) + ",'"
    sql += str(model_key) + "',"
    sql += str(last) + ","
    sql += str(highestBid) + ","
    sql += str(lowestAsk) + ","
    sql += str(output_rsi/1000.0) + ","
    sql += str(orderNumber) + ",'"
    sql += str(response) + "')"
    logger.debug("sql:{}".format(sql))
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
        
    except Exception as e:
        logger.error("Error data base: %s",str(e))
        logger.error("sql:%s",sql) 
        return False  
    return True

def logInsertNeighbors(logger,data_base_config,data):

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False
                             
    sql = "insert into log_neighbors(epoch,currency_code,currency_pair,mode,roc1,rsi,close,near_neighbors,neighbors,avg_benefit,"
    sql += "avg_benefit_weighted_space,avg_benefit_weighted_time,prob_win,q5_benefit,q95_benefit,"
    sql += "cheby2k,cheby2k_weighted_space,cheby2k_weighted_time,worse_expected,avg_space_distance,steps_mean,buy) values(" 
    sql += str(data['epoch'] ) + ","
    sql += str(data['currency_code'] ) + ",'"
    sql += data['currency_pair']  + "',"
    sql += str(data['mode']) + ","
    sql += str(data['roc1']) + ","
    sql += str(data['rsi']) + ","
    sql += str(data['close']) + ","
    sql += str(data['near_neighbors']) + ","
    sql += str(data['neighbors']) + ","
    sql += str(data['avg_benefit']) + ","
    sql += str(data['avg_benefit_weighted_space']) + ","
    sql += str(data['avg_benefit_weighted_time']) + ","
    sql += str(data['prob_win']) + ","
    sql += str(data['q5_benefit']) + ","
    sql += str(data['q95_benefit']) + ","
    sql += str(data['cheby2k']) + ","
    sql += str(data['cheby2k_weighted_space']) + ","
    sql += str(data['cheby2k_weighted_time']) + ","
    sql += str(data['worse_expected']) + ","
    sql += str(data['avg_space_distance']) + ","
    sql += str(data['steps_mean']) + ","
    sql += str(data['buy']) + ")"
    logger.debug("sql:{}".format(sql))
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
        
    except Exception as e:
        logger.error("Error data base: %s",str(e))
        logger.error("sql:%s",sql) 
        return False  
    return True

def logInsertOrder(logger,data_base_config,currency_pair,_type,price,amount_in_quote,amount_in_base,increment,model_name,model_key,last,highestBid,lowestAsk,mean_purchase_price,output_rsi,orderNumber,response):
    _type=_type
    model = model_name
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False
                             
    sql = "insert into log_orders(epoch,currency_pair,type,price,amount_in_quote,amount_in_base,model,increment,model_key,last,highestBid,lowestAsk,mean_purchase_price,output_rsi,orderNumber,response) values(" 
    sql += str(int(time.time())) + ",'"
    sql += currency_pair + "','"
    sql += _type + "',"
    sql += str(price) + ","
    sql += str(amount_in_quote) + ","
    sql += str(amount_in_base) + ",'"
    sql += model + "',"
    sql += str(increment) + ",'"
    sql += str(model_key) + "',"
    sql += str(last) + ","
    sql += str(highestBid) + ","
    sql += str(lowestAsk) + ","
    sql += str(mean_purchase_price) + ","
    sql += str(output_rsi/1000.0) + ","
    sql += str(orderNumber) + ",'"
    sql += str(response) + "')"
    logger.debug("sql:{}".format(sql))
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
        
    except Exception as e:
        logger.error("Error data base: %s",str(e))
        logger.error("sql:%s",sql) 
        return False  
    return True

def getLastTicketFromDBSimulating(logger,data_base_config,currency_pair,time_frame,now):

    delay = 10
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

    start_th = now - (288*time_frame)
    sql = "select last,lowestAsk,highestBid from tickets where " 
    sql += " currency_pair='" + currency_pair + "'"
    sql += " and epoch >" + str(start_th)
    sql += " and epoch <" + str(now+delay)
    sql += " order by epoch desc limit 1" 
    try:
      
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
            results = list(cursor.fetchall())
            if len(results) == 1:
                return results[0] 
            else:
                return False
    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False

def getTicketsFromDB(logger,data_base_config,currency_pair,start_th,end_th):


    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

   
    sql = "select epoch,currency_pair,last,lowestAsk,highestBid,ts from tickets where " 
    sql += " currency_pair='" + currency_pair + "'"
    sql += " and epoch >=" + str(start_th)
    sql += " and epoch <=" + str(end_th)
    sql += " order by epoch" 
    
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("%s",sql)
            cursor.execute(sql)
            results = list(cursor.fetchall())
            logger.debug("%s",results)
            if len(results) > 0:
                return results 
            else:
                logger.debug("no results")
                return False
       
    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False


def getCurrentMeanPurchaseFromDB(logger,data_base_config,currency_pair):


    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

    
    sql = "select mean_purchase_price from log_orders where type='buy' and " 
    sql += " currency_pair='" + currency_pair + "'"
    sql += " order by epoch desc limit 1" 
    
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("%s",sql)
            cursor.execute(sql)
            results = list(cursor.fetchall())
            logger.debug("%s",results)
            if len(results) == 1:
                return results[0] 
            else:
                logger.debug("no results")
                return False
       
    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False

def getLastTicketFromDB(logger,data_base_config,currency_pair,time_frame):


    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

    start_th = int(time.time()) - (288*time_frame)
    sql = "select last,lowestAsk,highestBid from tickets where " 
    sql += " currency_pair='" + currency_pair + "'"
    sql += " and epoch >" + str(start_th)
    sql += " order by epoch desc limit 1" 
    
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("%s",sql)
            cursor.execute(sql)
            results = list(cursor.fetchall())
            logger.debug("%s",results)
            if len(results) == 1:
                return results[0] 
            else:
                logger.debug("no results")
                return False
       
    except Exception as e:
        logger.error(sql)
        logger.error("Exception in sql:" + str(e))
        return False


def getLastCandlesFromDB(logger,data_base_config,currency_pair,time_frame):

    window = 300 

    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False

    start_th = int(time.time()) - (window*time_frame)
    sql = "select date,open,low,high,close from candles_" + str(time_frame) + " where " 
    sql += " code=" + str(codes[currency_pair] )
    sql += " and date >" + str(start_th)
    sql += " order by date asc" 
    
    try:
      
        with db_connection.cursor() as cursor:
            logger.debug("sql:{}".format(sql))
            cursor.execute(sql)
            results = list(cursor.fetchall())
            if len(results) > 288:
                return results
            else:
                logger.debug("No results!")
                return False
       
    except Exception as e:
        logger.error("sql:{} exception:{} ".format(sql,e))
        return False


def logInsertBalance(logger,data_base_config,data_for_log):
    try:
        db_connection = pymysql.connect(host=data_base_config['host'],
                             user=data_base_config['user'],
                             password=data_base_config['password'],
                             db=data_base_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
            logger.error("Error data base connection: %s",str(e))
            return False
                             
    sql = "insert into log_balances(epoch,currency,amount,btcs,percent) values(" 
    sql += str(data_for_log['epoch'] ) + ",'"
    sql += str(data_for_log['currency']) + "',"
    sql += str(data_for_log['amount']) + ","
    sql += str(data_for_log['btcs']) + ","
    sql += str(data_for_log['percent']) + ")"
    logger.debug("sql:{}".format(sql))
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
        db_connection.commit()
        
    except Exception as e:
        logger.error("Error data base: %s",str(e))
        logger.error("sql:%s",sql) 
        return False  
    return True
