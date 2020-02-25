import os
import pandas as pd
import numpy as np
import logging
from logging.handlers import TimedRotatingFileHandler
import time

initial_amount_to_buy_in_base = 200.0
min_amount_to_buy_in_base = 0.0
max_amount_to_buy_in_base = 100000
r = 0.02
min_rate = 0.02
fee = 0.002

def getTotalCurrentBaseInversion(purchase_operations):
    if len(purchase_operations) > 0:
        return np.sum([x[3] for x in purchase_operations])
    else:
        return 0.0


def getTotalCurrentQuoteInversion(purchase_operations):
    if len(purchase_operations) > 0:
        return np.sum([x[4] for x in purchase_operations])
    else:
        return 0.0

def get_amount_to_buy_in_quote(purchase_operations,purchase_price,initial_amount_to_buy_in_base,min_amount_to_buy_in_base,max_amount_to_buy_in_base,r):
    if len(purchase_operations) < 1:
        return initial_amount_to_buy_in_base/purchase_price
    purchase_prices = [x[0] for x in purchase_operations ]
    purchase_fees = [x[2] for x in purchase_operations ]
    purchase_amounts = [x[4] for x in purchase_operations ]
    real_purchase_operations = [] 
    for price,fee,amount in  zip(purchase_prices,purchase_fees,purchase_amounts):
        real_price = price + (price*fee)
        real_purchase_operations.append((real_price,amount))
    C = 0.0
    I = 0.0
    for p,a in real_purchase_operations:
        C += p*a
        I += a
    if C == 0:
        return 0
    amount_to_buy_in_quote = (C - (purchase_price*(1+r)*I))/(purchase_price*r)
   # print("calculating amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
    amount_to_buy_in_base = amount_to_buy_in_quote * purchase_price
  #  print("calculating amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
    if amount_to_buy_in_base < min_amount_to_buy_in_base:
        amount_to_buy_in_base = min_amount_to_buy_in_base
        amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price
    if amount_to_buy_in_base > max_amount_to_buy_in_base:
        amount_to_buy_in_base = max_amount_to_buy_in_base
        amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price

   # print("final amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
  #  print("final amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
    return amount_to_buy_in_quote

def getCurrentPercentBenefit(purchase_operations, current_sell_price):
    if len(purchase_operations) == 0:
        return 0
    purchase_prices = [x[0] for x in purchase_operations]
    purchase_fees = [x[2] for x in purchase_operations]
    purchase_amounts = [x[4] for x in purchase_operations]

    purchases = []
    total_amounts = 0.0

    for price, fee, amount in zip(purchase_prices, purchase_fees, purchase_amounts):
        real_price = price + (price*fee)
        total_amounts += amount
        purchases.append(real_price*amount)
    if total_amounts == 0:
        return 0
    average_purchase_price = np.sum(purchases) / total_amounts

    current_benefit = (current_sell_price/average_purchase_price) - 1.0
    return 100*current_benefit

def getCurrentRealMeanPrice(purchase_operations):
    if len(purchase_operations) == 0:
        return 0
    purchase_prices = [x[0] for x in purchase_operations]
    purchase_fees = [x[2] for x in purchase_operations]
    purchase_amounts = [x[4] for x in purchase_operations]
    real_purchase_operations = []
    for price, fee, amount in zip(purchase_prices, purchase_fees, purchase_amounts):
        real_price = price + (price*fee)
        real_purchase_operations.append((real_price, amount))
    num = 0.0
    den = 0.0
    for p, a in real_purchase_operations:
        num += p*a
        den += a
    if den == 0:
        return 0
    average_mean_price = num/den
    return average_mean_price


def sell(ticket,purchase_operations,base_balance,quote_balance,trade_operations):
    sell_price = ticket['highestBid'] 
    print("sell_price:{}".format(sell_price))
    amount_in_base = sum(quote_balance) * sell_price 
    print("amount to sell in quote currency:{}".format(sum(quote_balance)))
    print("amount to sell in base:{}".format(amount_in_base))
    total_amount_invested_in_base =  getTotalCurrentBaseInversion(purchase_operations)
    print("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
    current_percent_benefit = getCurrentPercentBenefit(purchase_operations,sell_price)
    print("current_percent_benefit:{}".format(current_percent_benefit))
    current_rate_benefit = current_percent_benefit/100.0
    print("current_rate_benefit:{}".format(current_rate_benefit))
    total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
    print("total_current_base_benefit:{}".format(total_current_base_benefit))
    purchase_operations.clear()
    trade_operations.append((total_amount_invested_in_base,total_current_base_benefit,current_rate_benefit))
    base_balance.append(total_amount_invested_in_base + total_current_base_benefit)
    quote_balance.append(-sum(quote_balance))


def buy(ticket,purchase_operations,base_balance,quote_balance):
    purchase_price = ticket['lowestAsk'] 
    if len(purchase_operations) == 0:
        amount_to_buy_in_base = initial_amount_to_buy_in_base
        amount_to_buy_in_quote  = initial_amount_to_buy_in_base / purchase_price
    else:
        current_mean_price = getCurrentRealMeanPrice(purchase_operations)
       # print("current_mean_price:{}".format(current_mean_price))
        delta_price_over_mean = (purchase_price/current_mean_price) - 1.0
       # print("delta_price_over_mean:{}".format(delta_price_over_mean))
        if delta_price_over_mean > -0.002:
            '''
            print("purchase_price:{}".format(purchase_price))
            print("current_mean_price:{}".format(current_mean_price))
            print("aborted buy not improve mean")
            print("delta_price_over_mean:{}".format(delta_price_over_mean))
            '''
            return
        amount_to_buy_in_quote = get_amount_to_buy_in_quote(purchase_operations,purchase_price,initial_amount_to_buy_in_base,min_amount_to_buy_in_base,max_amount_to_buy_in_base,r)
        amount_to_buy_in_base = amount_to_buy_in_quote * purchase_price
    '''
    print("we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
    print("we are gointo buy in base:{}".format(amount_to_buy_in_base))
    print("base_balance:{}".format(base_balance)) 
    print("quote_balance:{}".format(quote_balance))
    print("sum base_balance:{}".format(sum(base_balance))) 
    print("sum quote_balance:{}".format(sum(quote_balance)))
    '''
    if sum(base_balance) <= 10*min_amount_to_buy_in_base:
       # print("aborted buy by low balance")
       # print("sum base_balance:{}".format(sum(base_balance)))
        return

    if sum(base_balance) <=  amount_to_buy_in_base  :
        amount_to_buy_in_base = sum(base_balance)
        amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price
       # print("low balance revisited we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
      #  print("low balance revisited we are gointo buy in base:{}".format(amount_to_buy_in_base))
    purchase_operations.append((purchase_price,ticket['epoch'] ,fee,amount_to_buy_in_quote*purchase_price,amount_to_buy_in_quote))
    quote_balance.append(amount_to_buy_in_quote)
    base_balance.append(-amount_to_buy_in_quote*(purchase_price+fee))
    '''
    if amount_to_buy_in_base > 5.0:
        print("buy ticket ts:{}".format(ticket['ts']))
        print("amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
        print("sum base_balance:{}".format(sum(base_balance))) 
        print("sum quote_balance:{}".format(sum(quote_balance)))
    '''
        

def main(logger):
    start_time_simulation = 1559692800 #    Wednesday, June 5, 2019 0:00:00 BTC 7680
    end_time_simulation = 1574985600 #  Friday, November 29, 2019 0:00:00 BTC 7736 
    currency_pair = "USDC_BTC"
    day_before_learning = 100
    base_balance = []
    quote_balance = []
    purchase_operations =[]
    trade_operations = []
    repurchases = []
    games =  []
    sos_games = []
    base_balance.append(10000)
    quote_balance.append(0)
    time_start_sim = int(time.time())


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
    for index, ticket in tickets_df.iterrows():
        
        if (ticket['highestBid'] == ticket['lowestAsk']) and (ticket['highestBid'] == ticket['last'] ):
           # print(index,ticket['ts'],ticket['last'],ticket['highestBid'], ticket['lowestAsk'])
            buy(ticket,purchase_operations,base_balance,quote_balance)
        total_amount_invested_in_base =  getTotalCurrentBaseInversion(purchase_operations)
       # print("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
        current_percent_benefit = getCurrentPercentBenefit(purchase_operations,ticket['highestBid'])
       # print("current_percent_benefit:{}".format(current_percent_benefit))
        current_rate_benefit = current_percent_benefit/100.0
       # print("current_rate_benefit:{}".format(current_rate_benefit))
        total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
      #  if total_current_base_benefit > 10.0 and current_rate_benefit > 0.005:
        if current_rate_benefit > min_rate:
            print("sell:",index,ticket['ts'],ticket['last'],ticket['highestBid'], ticket['lowestAsk'])
            sell(ticket,purchase_operations,base_balance,quote_balance,trade_operations)
        '''
        if current_rate_benefit >  0.04:
            buy(ticket,purchase_operations,base_balance,quote_balance)
        '''
    
    time_end_sim = int(time.time())
    time_sim_in_seconds = time_end_sim - time_start_sim
    print("time_sim_in_seconds:{}".format(time_sim_in_seconds))
    
    max_inversion = max(trade_operations,key=lambda x:x[0])[0]
    print("max_inversion:{}".format(max_inversion))
    mean_inversion = np.mean([ x[0] for x in trade_operations ])
    print("mean_inversion:{}".format(mean_inversion))
    median_inversion = np.median([ x[0] for x in trade_operations ])
    print("median_inversion:{}".format(median_inversion))
   
    max_benefit = max(trade_operations,key=lambda x:x[1])[1]
    print("max_benefit:{}".format(max_benefit))
    mean_benefit= np.mean([ x[1] for x in trade_operations ])
    print("mean_benefit:{}".format(mean_benefit))

    total_benefit = sum( [ x[1] for x in trade_operations ] )
    print("total_benefit:{}".format(total_benefit))

    max_benefit_rate = max(trade_operations,key=lambda x:x[2])[2]
    print("max_benefit_rate:{}".format(max_benefit_rate))
    mean_benefit_rate= np.mean([ x[2] for x in trade_operations ])
    print("mean_benefit_rate:{}".format(mean_benefit_rate))



    
        

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