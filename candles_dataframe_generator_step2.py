import os
import pandas as pd
import time
import logging
import datetime
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
        tickets_df = pd.read_pickle("data/" + file_name_pkl)
    else:
        tickets = _db.getTicketsFromDB(logger,local_data_base_config,currency_pair,start_time_interest_data,end_time_simulation)
        tickets_df = pd.DataFrame(tickets)
        if not tickets_df.empty:               
            tickets_df.to_pickle("data/" + file_name_pkl )
            tickets_df.to_csv("data/" + file_name_csv )
    buffer_candles = []
    for value_start in range(start_time_interest_data, end_time_simulation, time_frame):

        b_start = value_start
        b_end = value_start + time_frame
        b_start_ts = datetime.datetime.fromtimestamp(b_start)
        b_end_ts = datetime.datetime.fromtimestamp(b_end)
        outside_values = tickets_df[tickets_df.epoch <= b_start]
        if outside_values.empty:
            continue
        open_value = outside_values.tail(1).iloc[0]['last']
        inside_values = tickets_df[(tickets_df.epoch >= b_start) & (tickets_df.epoch <= b_end)]
        if inside_values.empty:
            close_value = open_value
            min_value = open_value
            max_value = open_value
        else:
            close_value = inside_values.tail(1).iloc[0]['last']
            min_value = min([inside_values['last'].min(),open_value])
            max_value = max([inside_values['last'].max(),open_value])
        new_candle = {}
        new_candle['date'] = b_start
        new_candle['ts'] = datetime.datetime.utcfromtimestamp(b_start)
        new_candle['open'] = open_value
        new_candle['low'] = min_value
        new_candle['high'] = max_value
        new_candle['close'] = close_value
        buffer_candles.append(new_candle)
    file_name_pkl = "candles_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + "_"  + str(time_frame)  +".pkl"
    file_name_csv = "candles_"  + currency_pair + "_" + str(start_time_simulation) + "_" + str(end_time_simulation)  + "_"  + str(day_before_learning)  + "_"  + str(time_frame)  + ".csv"
    candles_df = pd.DataFrame(buffer_candles)
    if not candles_df.empty:               
        candles_df.to_pickle("data/" + file_name_pkl )
        candles_df.to_csv("data/" + file_name_csv )


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
    