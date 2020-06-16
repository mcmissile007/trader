from datetime import datetime
import time
import logging
import sys
from logging.handlers import TimedRotatingFileHandler


from database_config import remote_data_base_config
import aux_funcs as _aux
import poloniex_funcs as  _poloniex
import database_funcs as _db

CURRENCIES = ["USDC","BTC","ETH"]


def main(logger):
    
    last_signals = {}
    time_frame = 300
    buffer_data_for_log = [] 
    while (True):
        time.sleep(0.5)
        timeframes = _aux.decideCurrentTimeFrame(last_signals)
        if timeframes == []:
            continue
        logger.info("Start analyzing") 
        data_for_log ={}  
        now = int(time.time())
        data_for_log['epoch'] = now 
        mod = now % time_frame
        if mod != 0:
            logger.info("Error now time:%d",now)
            continue
        logger.info("analyzing:%s***",str(datetime.now()))
        available_balances = _poloniex.get_complete_available_balances(logger)
        if available_balances == False:
            logger.info("Error getting available_balances:{}".format(available_balances))
            time.sleep(60)
            continue
        buffer_data_for_log = [] 
        total_btcs = 0.0 
        for currency in available_balances:
            if currency in CURRENCIES: 
                logger.info("currency:{}".format(currency))
                logger.info("values:{}".format(available_balances[currency] ))
                amount_value = float(available_balances[currency]['available']) +  float(available_balances[currency]['onOrders']) 
                logger.info("amount_value:{}".format(amount_value))
                btc_value = float(available_balances[currency]['btcValue']) 
                logger.info("btc_value:{}".format(btc_value))
                data_for_log = {}
                data_for_log['epoch'] = now
                data_for_log['currency'] = currency
                data_for_log['amount'] = amount_value
                data_for_log['btcs'] = btc_value
                total_btcs += btc_value
                buffer_data_for_log.append(data_for_log)
        if total_btcs > 0:            
            for data in buffer_data_for_log:
                data['percent'] = data['btcs'] / total_btcs
                _db.logInsertBalance(logger,remote_data_base_config,data)

if __name__ == "__main__":
  
    run_file_name = sys.argv[0]
    if run_file_name.startswith ('/'):
        log_file_name = run_file_name.split('/')[-1].split('.')[0]  
    else:
        log_file_name = run_file_name
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(run_file_name)
    filename =  "./logs/" + run_file_name + "." + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main(logger)
