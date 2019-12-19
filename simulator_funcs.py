import database_funcs as _db
import purchase_operations_funcs as _purchase

def sim_buy_now (logger,local_data_base_config,currency_pair,time_frame,rate,amount,purchase_operations,base_balance,quote_balance,now):
    ticket = _db.getLastTicketFromDBSimulating(logger,local_data_base_config,currency_pair,time_frame,now)
    logger.debug("try to buy last ticket:{}".format(ticket))
    if ticket:
        rate = ticket['lowestAsk']
        # review fees
        purchase_operations.append((rate,now,0.002,amount*rate,amount))
        quote_balance.append(amount)
        base_balance.append(-amount*(rate+0.002))
        return True
    return False

def sim_buy_in_base (logger,local_data_base_config,currency_pair,close,increment,time_frame,output_rsi,model,purchase_operations,trade_operations,base_balance,quote_balance,now,repurchases):
    ticket = _db.getLastTicketFromDBSimulating(logger,local_data_base_config,currency_pair,time_frame,now)
    if ticket:
        last = ticket['last'] 
        lowestAsk = ticket['lowestAsk']
        purchase_loss = (lowestAsk/last) -1.0
        purchase_price = lowestAsk
        initial_amount_to_buy_in_base = float(model['initial_amount_to_buy_in_base'])
        min_amount_to_buy_in_base = float(model['min_amount_to_buy_in_base'])
        max_amount_to_buy_in_base = float(model['max_amount_to_buy_in_base'])
        logger.debug("purchase_price lowestAsk:{}".format(purchase_price))
        logger.debug("purchase_loss:{}".format(purchase_loss))
        logger.debug("initial amount to buy in base:{}".format(initial_amount_to_buy_in_base))
        logger.debug("min_amount_to_buy_in_base:{}".format(min_amount_to_buy_in_base))
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        logger.debug("purchase_operations:{}".format(purchase_operations))
        if len(purchase_operations) == 0:
            repurchases.append(0)
            amount_to_buy_in_base = initial_amount_to_buy_in_base
            amount_to_buy_in_quote  = amount_to_buy_in_base / purchase_price
            logger.debug("intial amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
            logger.debug("amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
        else:
            repurchases.append(1)
            current_mean_price = _purchase.getCurrentRealMeanPrice(purchase_operations)
            logger.debug("current_mean_price:{}".format(current_mean_price))
            delta_price_over_mean = (purchase_price/current_mean_price) - 1.0
            logger.debug("delta_price_over_mean:{}".format(delta_price_over_mean))
            if delta_price_over_mean > -0.002:
                logger.debug("purchase_price:{}".format(purchase_price))
                logger.debug("current_mean_price:{}".format(current_mean_price))
                logger.debug("aborted buy not improve mean")
                logger.debug("delta_price_over_mean:{}".format(delta_price_over_mean))
                return
            amount_to_buy_in_quote = _purchase.get_amount_to_buy_in_quote(logger,purchase_operations,purchase_price,initial_amount_to_buy_in_base,min_amount_to_buy_in_base,max_amount_to_buy_in_base,model['r'])
            amount_to_buy_in_base = amount_to_buy_in_quote * purchase_price
            logger.debug("we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
            logger.debug("we are gointo buy in base:{}".format(amount_to_buy_in_base))

        current_amount_invested = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("current_amount_invested:{}".format(current_amount_invested))
       
        logger.debug("base_balance:{}".format(base_balance)) 
        logger.debug("quote_balance:{}".format(quote_balance))
        logger.debug("sum base_balance:{}".format(sum(base_balance))) 
        logger.debug("sum quote_balance:{}".format(sum(quote_balance)))
        if sum(base_balance) <= 10*min_amount_to_buy_in_base:
            logger.debug("aborted buy by low balance")
            logger.debug("sum base_balance:{}".format(sum(base_balance)))
            return

        if sum(base_balance) <=  amount_to_buy_in_base  :
            amount_to_buy_in_base = sum(base_balance)
            amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price
            logger.debug("low balance revisited we are gointo buy in quote:{}".format(amount_to_buy_in_quote))
            logger.debug("low balance revisited we are gointo buy in base:{}".format(amount_to_buy_in_base))

        if purchase_loss < 0.015:
            response = sim_buy_now(logger,local_data_base_config,currency_pair,time_frame,purchase_price,amount_to_buy_in_quote,purchase_operations,base_balance,quote_balance,now) 
            logger.debug("sim_buy_now success:{} ".format(response))
            logger.debug("base_balance:{}".format(base_balance)) 
            logger.debug("quote_balance:{}".format(quote_balance))
            logger.debug("sum base_balance:{}".format(sum(base_balance))) 
            logger.debug("sum quote_balance:{}".format(sum(quote_balance)))
        else:
            pass
            logger.debug("no buyed exceed purchase_loss:{} ".format(purchase_price))

def sim_sell_SOS (logger,local_data_base_config,currency_pair,close,increment,time_frame,output_rsi,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,purchase_operations,trade_operations,quote_balance,now,sos_model_benefit,sos_games):
  
    ticket = _db.getLastTicketFromDBSimulating(logger,local_data_base_config,currency_pair,time_frame,now)
    logger.debug("try to sell last ticket:{}".format(ticket))
    if ticket:
    
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        amount_in_base = sum(quote_balance) * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(sum(quote_balance)))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        logger.debug("purchase_operations:{}".format(purchase_operations))
        total_amount_invested_in_base = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
        rate_amount = total_amount_invested_in_base / max_amount_to_buy_in_base
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        logger.debug("rate_amount:{}".format(rate_amount))
        current_percent_benefit = _purchase.getCurrentPercentBenefit(purchase_operations,sell_price)
        logger.debug("current_percent_benefit:{}".format(current_percent_benefit))
        current_rate_benefit = current_percent_benefit/100.0
        logger.debug("current_rate_benefit:{}".format(current_rate_benefit))
        total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
        logger.debug("total_current_base_benefit:{}".format(total_current_base_benefit))
        abs_rate_loss = abs(current_rate_benefit/(sell_loss+0.0001))
        logger.debug("abs rate_loss:{}".format(abs_rate_loss))
        if current_rate_benefit > sos_model_benefit:
            sell_price_limit = sell_price  - (sell_price*0.005)
            logger.debug("sell_price:{}".format(sell_price))
            logger.debug("sell_price_limit:{}".format(sell_price_limit))
            purchase_operations.clear()
            trade_operations.append((total_amount_invested_in_base,total_current_base_benefit,current_rate_benefit))
            base_balance.append(total_amount_invested_in_base + total_current_base_benefit)
            quote_balance.append(-sum(quote_balance))
            sos_games.append(1)

        else:
            pass
            logger.debug("current rate benefit not enough to SOS sell:{}".format(current_rate_benefit))

def sim_sell (logger,local_data_base_config,currency_pair,close,increment,time_frame,output_rsi,always_win,min_current_rate_benefit,max_amount_to_buy_in_base,base_balance,purchase_operations,trade_operations,quote_balance,now,games):
 
    ticket = _db.getLastTicketFromDBSimulating(logger,local_data_base_config,currency_pair,time_frame,now)
    logger.debug("try to sell last ticket:{}".format(ticket))
    if ticket:
     
        last = ticket['last'] 
        highestBid = ticket['highestBid']
        sell_loss = (last/highestBid) -1.0
        sell_price = highestBid
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_loss:{}".format(sell_loss))
        amount_in_base = sum(quote_balance) * sell_price 
        logger.debug("amount to sell in quote currency:{}".format(sum(quote_balance)))
        logger.debug("last rate:{}".format(ticket['last']))
        logger.debug("amount to sell in base:{}".format(amount_in_base))
        logger.debug("purchase_operations:{}".format(purchase_operations))
        total_amount_invested_in_base = _purchase.getTotalCurrentBaseInversion(purchase_operations)
        logger.debug("total_amount_invested_in_base:{}".format(total_amount_invested_in_base))
        rate_amount = total_amount_invested_in_base / max_amount_to_buy_in_base
        logger.debug("max_amount_to_buy_in_base:{}".format(max_amount_to_buy_in_base))
        logger.debug("rate_amount:{}".format(rate_amount))
        current_percent_benefit = _purchase.getCurrentPercentBenefit(purchase_operations,sell_price)
        logger.debug("current_percent_benefit:{}".format(current_percent_benefit))
        current_rate_benefit = current_percent_benefit/100.0
        logger.debug("current_rate_benefit:{}".format(current_rate_benefit))
        total_current_base_benefit = total_amount_invested_in_base * current_rate_benefit
        logger.debug("total_current_base_benefit:{}".format(total_current_base_benefit))
        abs_rate_loss = abs(current_rate_benefit/(sell_loss+0.0001))
        logger.debug("abs rate_loss:{}".format(abs_rate_loss))
        if always_win:
            if (current_rate_benefit < min_current_rate_benefit):
                logger.debug("aborted sell i want to win always:{}  and current benefit:{}".format(min_current_rate_benefit,current_rate_benefit))
                return
        rate_secure =  current_rate_benefit * 0.1   
        sell_price_limit = sell_price  - (sell_price*rate_secure)
        logger.debug("sell_price:{}".format(sell_price))
        logger.debug("sell_price_limit:{}".format(sell_price_limit))
        logger.debug("sell_price_limit:{}".format(sell_price_limit))
        purchase_operations.clear()
        trade_operations.append((total_amount_invested_in_base,total_current_base_benefit,current_rate_benefit))
        base_balance.append(total_amount_invested_in_base + total_current_base_benefit )
        quote_balance.append(-sum(quote_balance))
        games.append(1)
    