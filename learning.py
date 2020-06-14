import sys
from datetime import datetime
import time
import logging
from logging.handlers import TimedRotatingFileHandler

import aux_funcs as _aux
from learning_funcs import calculate_learning_dataframe_from_db

from database_config import remote_data_base_config
#CURRENCY_PAIRS = [("USDC_BTC",750,300),("USDC_ETH",760,300),("USDC_BCHSV",780,300),("USDC_XMR",760,300),("USDC_ATOM",770,300)]
CURRENCY_PAIRS = [("USDC_BTC",750,300),("USDC_ETH",760,300)]
DAYS_BEFORE = 100

if __name__ == "__main__":
  
    run_file_name = sys.argv[0]
    if run_file_name.startswith ('/'):
        log_file_name = run_file_name.split('/')[-1].split('.')[0]  
    else:
        log_file_name = run_file_name

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    filename =  "./logs/" + log_file_name + "." + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("START")
    logger.info("log_file_name:{}".format(log_file_name))
    while (True):
        logger.info("main call") 
        last_signals = {}
        for item in CURRENCY_PAIRS:
            currency_pair,output_rsi,time_frame = item 
            while (True):
                time.sleep(0.5)
                timeframes = _aux.decideCurrentTimeFrame(last_signals)
                if timeframes == []:
                    continue
                logger.debug("Start analyzing")    
                now = int(time.time())
                if now % time_frame != 0:
                    logger.debug("Error now time:%d",now)
                    continue
                time.sleep(10) #to have the last candle in database
                logger.debug("analyzing: %s %s ",currency_pair,str(datetime.now()))
                df = calculate_learning_dataframe_from_db(logger,remote_data_base_config,time_frame,currency_pair,output_rsi,now,DAYS_BEFORE)
                if not df.empty:
                    now = str(int(time.time()))
                    file_name_pkl = now + "_" + currency_pair + "_" + str(time_frame) + ".pkl"
                    file_name_csv = now + "_" + currency_pair + "_" + str(time_frame) + ".csv"
                    df.to_pickle("data/" + file_name_pkl )
                   # df.to_csv("data/" + file_name_csv )
                break
        logger.debug("long sleeping...")
        time.sleep(86400)

    logger.info("END")