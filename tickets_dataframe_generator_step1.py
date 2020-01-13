import os
import pandas as pd
import time
import logging
from logging.handlers import TimedRotatingFileHandler

currency_pair ="USDC_BTC"
start_time_simulation = 1559692800 #    Wednesday, June 5, 2019 0:00:00 BTC 7680
end_time_simulation = 1574985600 #  Friday, November 29, 2019 0:00:00 BTC 7736
day_before_learning = 100
time_frame = 300

from database_config import local_data_base_config

import database_funcs as _db


def main(logger):
    start_time_interest_data = start_time_simulation - (day_before_learning*86400)
    file_name_pkl = "tickets_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + ".pkl"
    file_name_csv = "tickets_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + ".csv"
    if os.path.exists("data/" + file_name_pkl):
        learning_df = pd.read_pickle("data/" + file_name_pkl)
    else:
        tickets = _db.getTicketsFromDB(logger,local_data_base_config,currency_pair,start_time_interest_data,end_time_simulation)
        tickets_df = pd.DataFrame(tickets)
        if not tickets_df.empty:               
            tickets_df.to_pickle("data/" + file_name_pkl )
            tickets_df.to_csv("data/" + file_name_csv )



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("simulating_" + str(int(time.time())) )
    log_file_name = "ticketc_dataframe_generator_" + str(int(time.time())) 
    filename =  "./logs/" + log_file_name + "." + str(int(time.time()))  + ".log"
    handler = TimedRotatingFileHandler(filename, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main(logger)
    