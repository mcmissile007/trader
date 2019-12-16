from datetime import datetime

def decideCurrentTimeFrame(last_signals):
    current_timeframes = []
    now = datetime.now()
    minute = int(now.minute)
    hour = int(now.hour)
    day = int(now.day)
    month = int(now.month)
    year = int(now.year)
    key = str(year) + "/" + str(month) + "/" + str(day) 
    key += " " + str(hour) + ":" +  str(minute)
    if key in last_signals:
            return []
    if minute == 0:
        last_signals[key] = True
        #check for signals in timesframes 300,900 y 1800
        current_timeframes.append(300)
        current_timeframes.append(900)
        current_timeframes.append(1800)
        
    else:
        if minute % 5 == 0:
            last_signals[key] = True
            #check for signals in timesframes 300
            current_timeframes.append(300)
            if minute % 15 == 0:
                #check for signals in timesframes 900
                current_timeframes.append(900)
                if minute == 30:
                    #check for signals in timesframes 1800
                    current_timeframes.append(1800)
    
    return current_timeframes   