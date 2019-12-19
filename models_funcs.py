
import random
import hashlib

def getModeltoTest():
    mode_sample = [3,5]
    always_win_sample = [True,False]
    r_sample =  [0.005,0.01]
    f_sample =  [0]
    avg_sample =  [0.02] 
    sos_model_benefit_sample =  [0.008,0.012] 
    amount_to_sos_mode_sample =  [100,1000] 
    max_amount_to_buy_in_base_sample =  [2000] 
    initial_amount_to_buy_in_base_sample = [5.0,50,200.0]  
    min_current_rate_benefit_sample =  [0.02] 

    model_to_test = {}
    #fixed
    model_to_test['currency_pair'] = "USDC_BTC" 
    model_to_test['sleep_time'] = 10 
    model_to_test['log_file_name'] = "learning_USDC_BTC_"
    model_to_test['min_amount_to_buy_in_base'] = 1.1
    model_to_test['n'] = -2
    model_to_test['ben_field'] = "b_750"
    model_to_test['min_roc1'] = 0.003
    model_to_test['max_roc1'] = 0.025
    model_to_test['rsi_mode'] = 1
    model_to_test['worse'] = -0.05
    model_to_test['cheby2k'] = -0.2
    model_to_test['steps'] =  566  
    model_to_test['features'] = {'roc1_z':1.0,'roc3_z':1.0,'roc6_z':1.0,'roc12_z':1.0,'roc24_z':1.0,'roc48_z':1.0,'roc72_z':1.0,'roc288_z':1.0,'sma50_delta_z':1.0,'ema13_delta_z':1.0,'ema26_delta_z':1.0,'trix_z':1.0,'rsi_z':1.0,'macd_z':1.0,'histogram_z':1.0} 
    
    model_to_test['always_win'] = random.choice(always_win_sample)
    model_to_test['mode'] = random.choice(mode_sample)
    model_to_test['r'] = random.choice(r_sample)
    model_to_test['func'] = random.choice(f_sample)
    model_to_test['avg'] = random.choice(avg_sample)
    model_to_test['sos_model_benefit'] = random.choice(sos_model_benefit_sample)
    model_to_test['amount_to_sos_mode'] = random.choice(amount_to_sos_mode_sample)
    model_to_test['max_amount_to_buy_in_base'] =  random.choice(max_amount_to_buy_in_base_sample) 
    model_to_test['initial_amount_to_buy_in_base'] =  random.choice(initial_amount_to_buy_in_base_sample) 
    model_to_test['min_current_rate_benefit'] =  random.choice(min_current_rate_benefit_sample)
    separator = "/"
    cadena = model_to_test['currency_pair'] + separator
    cadena += str(model_to_test['always_win']) + separator
    cadena += str(round(model_to_test['min_current_rate_benefit'],4)) + separator
    cadena += str(round(model_to_test['initial_amount_to_buy_in_base'],0)) + separator
    cadena += str(round(model_to_test['max_amount_to_buy_in_base'],0)) + separator
    cadena += str(round(model_to_test['min_amount_to_buy_in_base'],0)) + separator
    cadena += str(round(model_to_test['amount_to_sos_mode'],0)) + separator
    cadena += str(round(model_to_test['sos_model_benefit'],4)) + separator
    cadena += str(round(model_to_test['mode'],0)) + separator
    cadena += str(round(model_to_test['func'],0)) + separator
    cadena += str(round(model_to_test['avg'],4)) + separator
    cadena += str(round(model_to_test['r'],4)) + separator
    cadena += str(round(model_to_test['min_roc1'],4)) + separator
    cadena += str(round(model_to_test['max_roc1'],4)) + separator
    model_to_test['hash'] = hashlib.md5(cadena.encode('utf-8')).hexdigest()
    return model_to_test
