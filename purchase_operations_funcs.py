import numpy as np

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


def improveMeanPrice(purchase_operations, current_price):
    if len(purchase_operations) == 0:
        return True
    purchase_prices = [x[0] for x in purchase_operations]
    average_purchase_price = np.mean(purchase_prices)

    if current_price < (average_purchase_price - (average_purchase_price*0.002)):
        return True
    else:
        return False


def percentImproveMeanPrice(purchase_operations, current_price):
    if len(purchase_operations) == 0:
        return 0
    purchase_prices = [x[0] for x in purchase_operations]
    average_purchase_price = np.mean(purchase_prices)

    r = (current_price/average_purchase_price) - 1.0

    if r < 0:
        return abs(r)*100
    else:
        return 0


def getCurrentMeanPrice(purchase_operations):
    if len(purchase_operations) == 0:
        return 0
    purchase_prices = [x[0] for x in purchase_operations]
    average_purchase_price = np.mean(purchase_prices)
    return average_purchase_price


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


def get_amount_to_buy_in_quote(logger,purchase_operations,purchase_price,initial_amount_to_buy_in_base,min_amount_to_buy_in_base,max_amount_to_buy_in_base,r):
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
    logger.debug("calculating amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
    amount_to_buy_in_base = amount_to_buy_in_quote * purchase_price
    logger.debug("calculating amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
    if amount_to_buy_in_base < min_amount_to_buy_in_base:
        amount_to_buy_in_base = min_amount_to_buy_in_base
        amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price
    if amount_to_buy_in_base > max_amount_to_buy_in_base:
        amount_to_buy_in_base = max_amount_to_buy_in_base
        amount_to_buy_in_quote = amount_to_buy_in_base/purchase_price

    logger.debug("final amount_to_buy_in_base:{}".format(amount_to_buy_in_base))
    logger.debug("final amount_to_buy_in_quote:{}".format(amount_to_buy_in_quote))
    return amount_to_buy_in_quote
