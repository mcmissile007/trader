models = []
#USDC_BTC
'''
best results in bearish trend
start_time_simulation = 1559692800 #    Wednesday, June 5, 2019 0:00:00 BTC 7680
end_time_simulation = 1574985600 #  Friday, November 29, 2019 0:00:00 BTC 7736 

+--------------+------------+---------------+--------------+--------------+------------+--------+--------+-------+-------+-----------------+------------+-------------+----------------+-----------------+
| m_always_win | m_min_rate | m_init_amount | m_max_amount | m_sos_amount | m_sos_rate | m_mode | m_func | m_r   | m_avg | r_total_benefit | r_sos_rate | r_num_games | r_base_balance | r_quote_balance |
+--------------+------------+---------------+--------------+--------------+------------+--------+--------+-------+-------+-----------------+------------+-------------+----------------+-----------------+
|            1 |       0.02 |            50 |      1000000 |          200 |       0.01 |      3 |      0 | 0.005 | 0.015 |         5231.93 |       0.36 |          50 |    -0.00206817 |         1.78291 |
|            1 |       0.02 |            50 |      1000000 |         2000 |       0.01 |      3 |      0 | 0.005 | 0.015 |         5132.71 |       0.36 |          50 |    -0.00204477 |         1.77122 |
|            1 |       0.02 |            50 |      1000000 |          200 |       0.01 |      3 |      0 | 0.005 |  0.02 |         4369.71 |   0.357143 |          42 |   -0.000639995 |         1.75443 |
'''

''' with r_mode = 1 progessive r
+----------------------------------+---------------+--------+------------+--------+-------+-----------------+----------------+-----------------+-------------+-----------------+------------+
| m_hash                           | m_init_amount | m_mode | m_rsi_mode | m_r    | m_avg | r_total_benefit | r_base_balance | r_quote_balance | r_num_games | r_num_sos_games | r_sos_rate |
+----------------------------------+---------------+--------+------------+--------+-------+-----------------+----------------+-----------------+-------------+-----------------+------------+
| 6a0869e62639983ebf9cd3befb7461a3 |            50 |      3 |          0 | 0.0055 | 0.015 |         1450.69 |   -0.000498802 |         1.32834 |          51 |               1 |  0.0196078 |
| 8f4c25cf9ce07d0f948f801d4f4ca5cb |          1000 |      3 |          0 | 0.0055 | 0.015 |         1847.67 |   -0.000402209 |        0.965659 |          17 |               1 |  0.0588235 |
| a772a17f21ea58f4ad2af5ef4504bd25 |           500 |      3 |          0 | 0.0055 | 0.015 |         2123.46 |   -0.000342796 |         1.11256 |          24 |               6 |       0.25 |
| 2fd5f1b0abc7a3f015d09e8b0057d8c0 |           100 |      3 |          0 | 0.0055 | 0.015 |         2271.98 |   -0.000106329 |         1.34637 |          48 |               3 |     0.0625 |
| 7207062453b6b5d558e8ffef946891dc |           600 |      3 |          0 | 0.0055 | 0.015 |         2302.11 |    -0.00139333 |         1.11861 |          24 |               5 |   0.208333 |
| 0a1dc897d0df897893157e6dfcdcc422 |           800 |      3 |          0 | 0.0055 | 0.015 |         2353.15 |    -0.00080199 |         1.01264 |          22 |               4 |   0.181818 |
| 1201a26c525197489826ac7b7ae5af9b |           200 |      3 |          0 | 0.0055 | 0.015 |         3762.47 |        160.075 |         1.76177 |          46 |               7 |   0.152174 |
| e49c73c81b93854306c70162c1e57f43 |           400 |      3 |          0 | 0.0055 | 0.015 |         4608.89 |   -0.000407152 |         1.69934 |          42 |              12 |   0.285714 |
+----------------------------------+---------------+--------+------------+--------+-------+-----------------+----------------+-----------------+-------------+-----------------+------------+
'''
models = []
#BTC
model = {}
model['always_win'] = True
model['min_current_rate_benefit'] = 0.02
model['currency_pair'] = "USDC_BTC" 
model['sleep_time'] = 10  + len(models)
model['log_file_name'] = "trader_USDC_BTC_"
model['initial_base_balance_to_simulate'] = 10000.0
model['initial_amount_to_buy_in_base'] = 200.0  
model['min_amount_to_buy_in_base'] = 1.1 
model['max_amount_to_buy_in_base'] = 1000000.0
model['sos_amount'] = 200.0
model['sos_rate'] = 0.01
model['func'] = 0
model['r'] = 0.005
model['r_mode'] = 2
model['avg'] = 0.015
model['n'] = -2
model['ben_field'] = "b_750"
model['min_roc1'] = 0.003
model['max_roc1'] = 0.025
model['rsi_mode'] = 0
model['mode'] = 3 
model['worse'] = -0.05
model['cheby2k'] = -0.2
model['steps'] =  566  
model['features'] = {'roc1_z':1.0,'roc3_z':1.0,'roc6_z':1.0,'roc12_z':1.0,'roc24_z':1.0,'roc48_z':1.0,'roc72_z':1.0,'roc288_z':1.0,'sma50_delta_z':1.0,'ema13_delta_z':1.0,'ema26_delta_z':1.0,'trix_z':1.0,'rsi_z':1.0,'macd_z':1.0,'histogram_z':1.0} 
models.append(model)
#ETH
model = {}
model['always_win'] = True
model['min_current_rate_benefit'] = 0.02
model['currency_pair'] = "USDC_ETH" 
model['sleep_time'] = 12  + len(models)
model['log_file_name'] = "trader_USDC_ETH_"
model['initial_base_balance_to_simulate'] = 10000.0
model['initial_amount_to_buy_in_base'] = 200.0  
model['min_amount_to_buy_in_base'] = 1.1 
model['max_amount_to_buy_in_base'] = 1000000.0
model['sos_amount'] = 200.0
model['sos_rate'] = 0.01
model['func'] = 0
model['r'] = 0.005
model['r_mode'] = 2
model['avg'] = 0.02
model['n'] = -2
model['ben_field'] = "b_760"
model['min_roc1'] = 0.003
model['max_roc1'] = 0.025
model['rsi_mode'] = 0
model['mode'] = 3 
model['worse'] = -0.05
model['cheby2k'] = -0.2
model['steps'] =  566  
model['features'] = {'roc1_z':1.0,'roc3_z':1.0,'roc6_z':1.0,'roc12_z':1.0,'roc24_z':1.0,'roc48_z':1.0,'roc72_z':1.0,'roc288_z':1.0,'sma50_delta_z':1.0,'ema13_delta_z':1.0,'ema26_delta_z':1.0,'trix_z':1.0,'rsi_z':1.0,'macd_z':1.0,'histogram_z':1.0} 
models.append(model)
#balance.py and learning.py must be update when add a new currency
