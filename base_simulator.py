import os
import pandas as pd
import numpy as np
import logging
from logging.handlers import TimedRotatingFileHandler
import time

def main(logger):
    start_time_simulation = 1559692800 #    Wednesday, June 5, 2019 0:00:00 BTC 7680
    end_time_simulation = 1574985600 #  Friday, November 29, 2019 0:00:00 BTC 7736 
    currency_pair = "USDC_BTC"
    day_before_learning = 100
    file_name_pkl = "tickets_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + ".pkl"
    if os.path.exists("data/" + file_name_pkl):
        tickets_df = pd.read_pickle("data/" + file_name_pkl)
    else:
        logger.error(f"Error reading tickets dataframe:no file data")
        return
    if tickets_df.empty:
        logger.error(f"Error reading tickets dataframe,empty dataframe")
        return
    print(tickets_df.head())
    print(tickets_df.tail())

if __name__ == "__main__":
    logger = logging.getLogger("fast_simulating")
    log_file_name = "fast_simulating"
    filename =  "./logs/" + log_file_name + "_" + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main(logger)