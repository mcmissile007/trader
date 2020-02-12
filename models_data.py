models = []
#USDC_BTC
'''
best results
 m_always_win | m_min_rate | m_init_amount | m_max_amount | m_sos_amount | m_sos_rate | m_mode | m_func | m_r   | m_avg | r_total_benefit | r_sos_rate | r_num_games | r_base_balance | r_quote_balance |
+--------------+------------+---------------+--------------+--------------+------------+--------+--------+-------+-------+-----------------+------------+-------------+----------------+-----------------+
|            0 |      0.025 |           200 |         6000 |         1000 |       0.01 |      3 |      0 |  0.01 | 0.015 |         3273.34 |   0.243243 |          74 |         9273.3 |               0 |
|            0 |      0.015 |           200 |      1000000 |          100 |       0.01 |      3 |      0 |  0.01 | 0.015 |         3270.95 |   0.226667 |          75 |        9270.92 |               0 |
|            0 |       0.02 |            50 |      1000000 |         2000 |       0.01 |      3 |      0 | 0.005 | 0.015 |          3221.3 |   0.257576 |          66 |        9221.27 |               0 |
selected the third one because  r_num_games is lower so  lower fees
'''

model = {}
model['always_win'] = False
model['min_current_rate_benefit'] = 0.02
model['currency_pair'] = "USDC_BTC" 
model['sleep_time'] = 10  + len(models)
model['log_file_name'] = "trader_USDC_BTC_"
model['initial_base_balance_to_simulate'] = 6000.0
model['initial_amount_to_buy_in_base'] = 50.0 
model['min_amount_to_buy_in_base'] = 1.1
model['max_amount_to_buy_in_base'] = 1000000.0
model['sos_amount'] = 2000.0
model['sos_rate'] = 0.01
model['func'] = 0
model['r'] = 0.005
model['avg'] = 0.015
model['n'] = -2
model['ben_field'] = "b_750"
model['min_roc1'] = 0.003
model['max_roc1'] = 0.025
model['rsi_mode'] = 1
model['mode'] = 3 
model['worse'] = -0.05
model['cheby2k'] = -0.2
model['steps'] =  566  
model['features'] = {'roc1_z':1.0,'roc3_z':1.0,'roc6_z':1.0,'roc12_z':1.0,'roc24_z':1.0,'roc48_z':1.0,'roc72_z':1.0,'roc288_z':1.0,'sma50_delta_z':1.0,'ema13_delta_z':1.0,'ema26_delta_z':1.0,'trix_z':1.0,'rsi_z':1.0,'macd_z':1.0,'histogram_z':1.0} 
models.append(model)
