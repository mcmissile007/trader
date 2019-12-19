models = []
#USDC_BTC  
model = {}
model['always_win'] = True
model['min_current_rate_benefit'] = 0.02
model['currency_pair'] = "USDC_BTC" 
model['sleep_time'] = 10  + len(models)
model['log_file_name'] = "trader_USDC_BTC_"
model['initial_amount_to_buy_in_base'] = 5.0 
model['min_amount_to_buy_in_base'] = 1.1
model['max_amount_to_buy_in_base'] = 1000.0
model['sos_amount'] = 100.0
model['sos_rate'] = 0.008
model['func'] = 0
model['r'] = 0.005
model['avg'] = 0.02
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
