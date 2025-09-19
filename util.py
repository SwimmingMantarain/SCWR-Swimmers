from datetime import time, date

def fmt_time(tim_e: time) -> str:
    if tim_e.hour:
        return tim_e.strftime("%H:%M:%S.%f")[:-3]
    elif tim_e.minute:
        return tim_e.strftime("%M:%S.%f")[:-3]
    else:
        return tim_e.strftime("%S.%f")[:-3]

def fmt_date(dat_e: date) -> str:
    return dat_e.strftime("%d-%m-%Y")
