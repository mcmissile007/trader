import numpy as np


def get_rsi(series, period):#OK 
    delta = series.diff().dropna()
    u = delta.where(delta > 0).fillna(0)
    d = delta.where(delta < 0).fillna(0).abs()
    u[u.index[period-1]] = np.mean( u[:period] ) 
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] )
    d = d.drop(d.index[:(period-1)])
    u_ema =  u.ewm(com=period-1, adjust=False).mean()
    d_ema = d.ewm(com=period-1, adjust=False).mean()
    rsi = u_ema / (u_ema + d_ema)
    return rsi

def weighted_avg_and_std(values, weights):
   
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return (average, np.sqrt(variance))