import database_funcs as _db
import numpy as np

import math_funcs as _mth

from currency_codes import codes

def simpleShouldIInvest(logger,learning_df,last_candle_df,model,epoch,currency_pair,data_base_config = None):
    IMPORTANT_FEATURES=model['features'] 
    N = model['n'] 
    AVG_TH = model['avg'] 
    CHEBY_2K_TH = model['cheby2k'] 
    WORSE_TH = model['worse'] 
    BEN_FIELD = model['ben_field'] 
    MODE = model['mode'] 
    STEP_FIELD =  "step_" + BEN_FIELD.split('_')[1] 
    RSI_MODE = model['rsi_mode']
    MIN_ROC1 = model['min_roc1'] 
    MAX_ROC1 = model['max_roc1'] 
    STEPS_TH = model['steps'] 
    OUTPUT_RSI_VALUE = int(BEN_FIELD.split("_")[1])/1000.0
    INPUT_RSI_VALUE_TH = OUTPUT_RSI_VALUE- (OUTPUT_RSI_VALUE*0.05)
    data_for_log = {} 

    #logger.debug("N:{} AVG_TH:{} CHEBY_2K_TH:{} WORSE_TH:{} BEN_FIELD:{} MODE:{}".format(N,AVG_TH,CHEBY_2K_TH,WORSE_TH,BEN_FIELD,MODE))
    #logger.debug("STEP_FIELD:{} RSI_MODE:{} MIN_ROC1:{} MAX_ROC1:{} STEPS_TH:{} ".format(STEP_FIELD,RSI_MODE,MIN_ROC1,MAX_ROC1,STEPS_TH))
    #logger.debug("OUTPUT_RSI_VALUE:{} INPUT_RSI_VALUE_TH:{}".format(OUTPUT_RSI_VALUE,INPUT_RSI_VALUE_TH))
    
    data_for_log['epoch'] = epoch
    data_for_log['currency_pair'] = currency_pair
    data_for_log['currency_code'] = codes[currency_pair] 
    data_for_log['mode'] = MODE
    data_for_log['roc1'] = last_candle_df.iloc[0]['roc1']
    data_for_log['rsi'] =  last_candle_df.iloc[0]['rsi']
    data_for_log['close'] =  last_candle_df.iloc[0]['close']
    data_for_log['near_neighbors'] = 0
    data_for_log['neighbors'] = 0
    data_for_log['avg_benefit'] = 0.0
    data_for_log['avg_benefit_weighted_space'] = 0.0
    data_for_log['avg_benefit_weighted_time'] = 0.0
    data_for_log['prob_win'] = 0.0
    data_for_log['q5_benefit'] = 0.0
    data_for_log['q95_benefit'] = 0.0
    data_for_log['cheby2k'] = 0.0
    data_for_log['cheby2k_weighted_space'] = 0.0
    data_for_log['cheby2k_weighted_time'] = 0.0
    data_for_log['worse_expected'] = 0.0
    data_for_log['steps_mean'] = 0
    data_for_log['buy'] = 0 
    data_for_log['avg_space_distance'] = 0.0
    if abs(last_candle_df.iloc[0]['roc1'])  < MAX_ROC1:
        logger.debug("abs roc1:{} lower than:{}".format(last_candle_df.iloc[0]['roc1'],MAX_ROC1))
        return False
    else:
        data_for_log['buy'] = 1
        logger.debug("roc1:{} less than:{} you must buy!".format(last_candle_df.iloc[0]['roc1'],-MAX_ROC1))
        if data_base_config != None:
            _db.logInsertNeighbors(logger,data_base_config,data_for_log)
        return True

def simpleDownShouldIInvest(logger,learning_df,last_candle_df,model,epoch,currency_pair,data_base_config = None):
    IMPORTANT_FEATURES=model['features'] 
    N = model['n'] 
    AVG_TH = model['avg'] 
    CHEBY_2K_TH = model['cheby2k'] 
    WORSE_TH = model['worse'] 
    BEN_FIELD = model['ben_field'] 
    MODE = model['mode'] 
    STEP_FIELD =  "step_" + BEN_FIELD.split('_')[1] 
    RSI_MODE = model['rsi_mode']
    MIN_ROC1 = model['min_roc1'] 
    MAX_ROC1 = model['max_roc1'] 
    STEPS_TH = model['steps'] 
    OUTPUT_RSI_VALUE = int(BEN_FIELD.split("_")[1])/1000.0
    INPUT_RSI_VALUE_TH = OUTPUT_RSI_VALUE- (OUTPUT_RSI_VALUE*0.05)
    data_for_log = {} 

    logger.debug("N:{} AVG_TH:{} CHEBY_2K_TH:{} WORSE_TH:{} BEN_FIELD:{} MODE:{}".format(N,AVG_TH,CHEBY_2K_TH,WORSE_TH,BEN_FIELD,MODE))
    logger.debug("STEP_FIELD:{} RSI_MODE:{} MIN_ROC1:{} MAX_ROC1:{} STEPS_TH:{} ".format(STEP_FIELD,RSI_MODE,MIN_ROC1,MAX_ROC1,STEPS_TH))
    logger.debug("OUTPUT_RSI_VALUE:{} INPUT_RSI_VALUE_TH:{}".format(OUTPUT_RSI_VALUE,INPUT_RSI_VALUE_TH))


    data_for_log['epoch'] = epoch
    data_for_log['currency_pair'] = currency_pair
    data_for_log['currency_code'] = codes[currency_pair] 
    data_for_log['mode'] = MODE
    data_for_log['roc1'] = last_candle_df.iloc[0]['roc1']
    data_for_log['rsi'] =  last_candle_df.iloc[0]['rsi']
    data_for_log['close'] =  last_candle_df.iloc[0]['close']
    data_for_log['near_neighbors'] = 0
    data_for_log['neighbors'] = 0
    data_for_log['avg_benefit'] = 0.0
    data_for_log['avg_benefit_weighted_space'] = 0.0
    data_for_log['avg_benefit_weighted_time'] = 0.0
    data_for_log['prob_win'] = 0.0
    data_for_log['q5_benefit'] = 0.0
    data_for_log['q95_benefit'] = 0.0
    data_for_log['cheby2k'] = 0.0
    data_for_log['cheby2k_weighted_space'] = 0.0
    data_for_log['cheby2k_weighted_time'] = 0.0
    data_for_log['worse_expected'] = 0.0
    data_for_log['steps_mean'] = 0
    data_for_log['buy'] = 0 
    data_for_log['avg_space_distance'] = 0.0
    if last_candle_df.iloc[0]['roc1']  > -MAX_ROC1:
        logger.debug("roc1:{} bigger than:{}".format(last_candle_df.iloc[0]['roc1'],-MAX_ROC1))
        return False
    else:
        data_for_log['buy'] = 1
        logger.debug("roc1:{} less than:{} you must buy!".format(last_candle_df.iloc[0]['roc1'],-MAX_ROC1))
        if data_base_config != None:
            _db.logInsertNeighbors(logger,data_base_config,data_for_log)
        return True


def shouldIInvest(logger,learning_df,last_candle_df,model,epoch,currency_pair,data_base_config = None):
    IMPORTANT_FEATURES=model['features'] 
    N = model['n'] 
    AVG_TH = model['avg'] 
    CHEBY_2K_TH = model['cheby2k'] 
    WORSE_TH = model['worse'] 
    BEN_FIELD = model['ben_field'] 
    MODE = model['mode'] 
    STEP_FIELD =  "step_" + BEN_FIELD.split('_')[1] 
    RSI_MODE = model['rsi_mode']
    MIN_ROC1 = model['min_roc1'] 
    MAX_ROC1 = model['max_roc1'] 
    STEPS_TH = model['steps'] 
    OUTPUT_RSI_VALUE = int(BEN_FIELD.split("_")[1])/1000.0
    INPUT_RSI_VALUE_TH = OUTPUT_RSI_VALUE- (OUTPUT_RSI_VALUE*0.05)
    data_for_log = {} 
      

    #logger.debug("N:{} AVG_TH:{} CHEBY_2K_TH:{} WORSE_TH:{} BEN_FIELD:{} MODE:{}".format(N,AVG_TH,CHEBY_2K_TH,WORSE_TH,BEN_FIELD,MODE))
    #logger.debug("STEP_FIELD:{} RSI_MODE:{} MIN_ROC1:{} MAX_ROC1:{} STEPS_TH:{} ".format(STEP_FIELD,RSI_MODE,MIN_ROC1,MAX_ROC1,STEPS_TH))
    #logger.debug("OUTPUT_RSI_VALUE:{} INPUT_RSI_VALUE_TH:{}".format(OUTPUT_RSI_VALUE,INPUT_RSI_VALUE_TH))

    data_for_log['epoch'] = epoch
    data_for_log['currency_pair'] = currency_pair
    data_for_log['currency_code'] = codes[currency_pair] 
    data_for_log['mode'] = MODE
    data_for_log['roc1'] = last_candle_df.iloc[0]['roc1']
    data_for_log['rsi'] =  last_candle_df.iloc[0]['rsi']
    data_for_log['close'] =  last_candle_df.iloc[0]['close']
    data_for_log['near_neighbors'] = 0
    data_for_log['neighbors'] = 0
    data_for_log['avg_benefit'] = 0.0
    data_for_log['avg_benefit_weighted_space'] = 0.0
    data_for_log['avg_benefit_weighted_time'] = 0.0
    data_for_log['prob_win'] = 0.0
    data_for_log['q5_benefit'] = 0.0
    data_for_log['q95_benefit'] = 0.0
    data_for_log['cheby2k'] = 0.0
    data_for_log['cheby2k_weighted_space'] = 0.0
    data_for_log['cheby2k_weighted_time'] = 0.0
    data_for_log['worse_expected'] = 0.0
    data_for_log['steps_mean'] = 0
    data_for_log['buy'] = 0 
    data_for_log['avg_space_distance'] = 0.0
    if np.abs(last_candle_df.iloc[0]['roc1']  ) < MIN_ROC1:
        logger.debug("abs roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MIN_ROC1))
        return False

    if RSI_MODE == 1:
        
        if last_candle_df.iloc[0]['rsi'] > INPUT_RSI_VALUE_TH:
            logger.debug("rsi_mode 1")
            logger.debug("rsi:{} bigger than:{}".format(last_candle_df.iloc[0]['rsi'],INPUT_RSI_VALUE_TH))
            if data_base_config != None:
                _db.logInsertNeighbors(logger,data_base_config,data_for_log)
            return False

        
    if MODE == 1:     
        if abs(last_candle_df.iloc[0]['roc1'])  > MAX_ROC1:
            logger.debug("abs roc1:{} greater than:{} you must buy!".format(last_candle_df.iloc[0]['roc1'],MAX_ROC1))
            return True
        if last_candle_df.iloc[0]['roc1'] < MIN_ROC1:
            logger.debug("roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MIN_ROC1))
            return False
    if MODE == 2:
         if last_candle_df.iloc[0]['roc1'] < MIN_ROC1:
            logger.debug("roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MIN_ROC1))
            return False
    if MODE == 3:
        if abs(last_candle_df.iloc[0]['roc1']) < MIN_ROC1:
            logger.debug("abs roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MIN_ROC1))
            return False
        if abs(last_candle_df.iloc[0]['roc1'])  > MAX_ROC1:
            data_for_log['buy'] = 1
            logger.debug("abs roc1:{} greater than:{} you must buy!".format(last_candle_df.iloc[0]['roc1'],MAX_ROC1))
            if data_base_config != None:
                _db.logInsertNeighbors(logger,data_base_config,data_for_log)
            return True
    if MODE == 4:
        if last_candle_df.iloc[0]['roc1']  > MAX_ROC1:
            logger.debug("roc1:{} greater than:{} you must buy!".format(last_candle_df.iloc[0]['roc1'],MAX_ROC1))
            return True
        if abs(last_candle_df.iloc[0]['roc1']) < MIN_ROC1:
            logger.debug("abs roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MIN_ROC1))
            return False
        if last_candle_df.iloc[0]['roc1'] < MAX_ROC1:#zona D no se analiza 
            logger.debug("roc1:{} less than:{}".format(last_candle_df.iloc[0]['roc1'],MAX_ROC1))
            return False
  
    
    train = learning_df.copy(deep = True)
    s = 0.0
    for feature in  IMPORTANT_FEATURES:
        s += IMPORTANT_FEATURES[feature] * ((last_candle_df.iloc[0][feature] - train[feature] + 0.00001 ) **2)

    train['space_distance'] = np.sqrt(s)
    train['w_space_distance'] = 100 - train['space_distance'] 
    train['time_distance'] = last_candle_df.iloc[0]['date'] - train['date']
    train = train[train['space_distance'].notnull()] 
    train.sort_values('space_distance',ascending=True,inplace=True) 
    logger.debug("{}".format(train.head(5).T))

    if N == 0:
        n = 0
        for j, row in train.iterrows():
            if row['space_distance']  > np.sqrt(len(IMPORTANT_FEATURES)):
                break
            n += 1
    elif N == -1:
        n = 0
        for j, row in train.iterrows():
            if row['space_distance']  > np.sqrt(len(IMPORTANT_FEATURES)/2):
                break
            n += 1
    elif N == -2:
        n = 0
        for j, row in train.iterrows():
            if row['space_distance']  > np.sqrt(2):
                break
            n += 1
    elif N == -3:
        n = 0
        for j, row in train.iterrows():
            if row['space_distance']  > 1.0:
                break
            n += 1
    else:
            n = N
    logger.debug("n:{}".format(n))
    data_for_log['near_neighbors'] =  n
    if n == 0:
        logger.debug("no neighbors for this point")
        n = 5 #the closest neighbors
      
    neighbors = train[:n]
    logger.debug("len_neighbors:{}".format(len(neighbors)))
    data_for_log['neighbors'] =  len(neighbors)
    if len(neighbors) < 1:
        logger.debug("len_neighbors less than 1")
        return False
    avg_benefit = neighbors[BEN_FIELD].mean()
    avg_space_distance = neighbors["space_distance"].mean()
    if n > 1:
        avg_benefit_weighted_space,std_benefit_weighted_space = _mth.weighted_avg_and_std(neighbors[BEN_FIELD].values,neighbors.w_space_distance.values)
        avg_benefit_weighted_time,std_benefit_weighted_time = _mth.weighted_avg_and_std(neighbors[BEN_FIELD].values,neighbors.time_distance.values)
    else:
        avg_benefit_weighted_space = avg_benefit
        std_benefit_weighted_space = 0
        avg_benefit_weighted_time = avg_benefit
        std_benefit_weighted_time = 0

    steps_mean = neighbors[STEP_FIELD].mean()
    
    min_benefit = neighbors[BEN_FIELD].min()
    max_benefit = neighbors[BEN_FIELD].max()
    if n > 1:
        std_benefit = neighbors[BEN_FIELD].std()
    else:
        std_benefit = 0

    cheby2k = avg_benefit - (2*std_benefit)
    cheby2k_weighted_time = avg_benefit_weighted_time - (2*std_benefit_weighted_time)
    cheby2k_weighted_space = avg_benefit_weighted_space - (2*std_benefit_weighted_space)
    q5_benefit = neighbors[BEN_FIELD].quantile(0.05)
    q95_benefit = neighbors[BEN_FIELD].quantile(0.95)
    
    wins = np.where(neighbors[BEN_FIELD] > 0,1,0).sum()
    if n > 0:
        prob_win = wins/n
    else:
        prob_win = 0.0
    worse_expected = prob_win * avg_benefit_weighted_space  + ((1-prob_win)*min_benefit)

    quantile_cond = False
    average_condition = False
    cheby2k_condition = False
    worse_condition = False
    steps_condition = False


    logger.debug("last_candle_df:{}".format(last_candle_df[['tm','close','roc1','roc3','roc6','roc12']]))
    logger.debug("last_candle_df:{}".format(last_candle_df[['roc48','roc72','rsi']]))

    logger.debug("neighbors:{}".format(neighbors[['tm','close','roc1','roc3','roc6','roc12']]))

    logger.debug("neighbors:{}".format(neighbors[['roc48','roc72','rsi','space_distance']]))

    logger.debug("avg_benefit:{}".format(avg_benefit))
    logger.debug("avg_benefit_weighted_space:{}".format(avg_benefit_weighted_space))
    logger.debug("avg_benefit_weighted_time:{}".format(avg_benefit_weighted_time))
    logger.debug("prob_win:{}".format(prob_win))
    logger.debug("q5_benefit:{}".format(q5_benefit))
    logger.debug("q95_benefit:{}".format(q95_benefit))
    data_for_log['avg_benefit'] =  avg_benefit
    data_for_log['avg_benefit_weighted_space'] =  avg_benefit_weighted_space
    data_for_log['avg_benefit_weighted_time'] =  avg_benefit_weighted_time
    data_for_log['prob_win'] =  prob_win
    data_for_log['q5_benefit'] =  q5_benefit
    data_for_log['q95_benefit'] =  q95_benefit
    data_for_log['cheby2k'] =  cheby2k
    data_for_log['cheby2k_weighted_time'] =  cheby2k_weighted_time
    data_for_log['cheby2k_weighted_space'] =  cheby2k_weighted_space
    data_for_log['worse_expected'] =  worse_expected
    data_for_log['steps_mean'] =  steps_mean
    data_for_log['avg_space_distance'] =  avg_space_distance

    logger.debug("data_for_log:{}".format(data_for_log))


    
    if q95_benefit > 0:
        if q95_benefit + q5_benefit > 0:
            quantile_cond = True
    
    if avg_benefit > AVG_TH and avg_benefit_weighted_space > AVG_TH and avg_benefit_weighted_time > AVG_TH:
        average_condition = True

    if cheby2k  > CHEBY_2K_TH and cheby2k_weighted_time  > CHEBY_2K_TH and  cheby2k_weighted_space  > CHEBY_2K_TH :
        cheby2k_condition = True
    if worse_expected > WORSE_TH:
        worse_condition = True
    if steps_mean < STEPS_TH:
        steps_condition = True
    

    buy = False
    logger.debug("average_condition:{}".format(average_condition))
    logger.debug("cheby2k_condition:{}".format(cheby2k_condition))
    logger.debug("worse_condition:{}".format(worse_condition))
    logger.debug("steps_condition:{}".format(steps_condition))
    logger.debug("quantile_cond:{}".format(quantile_cond))
    
    if cheby2k_condition  and average_condition and quantile_cond and worse_condition and steps_condition:
        buy = True
        data_for_log['buy'] = 1 
        
    else:
        buy = False
        logger.debug("wait to buy...")
        data_for_log['buy']= 0 
    if data_base_config != None:
        _db.logInsertNeighbors(logger,data_base_config,data_for_log)

    return buy