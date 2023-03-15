from datetime import timedelta
from re import findall, match

def timedelta_format(days: int, hours : int, minutes : int, seconds : int):
    return timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)

def convert_to_date(seconds : float):
    time_format = str(timedelta(seconds = seconds))
    return time_format

def covert_str_to_seconds(str_time : str):
    time_units = {
        "s" : 1,
        "m" : 60,
        "h" : 3600,
        "d" : 24 * 3600
    }
    
    unit = str_time[-1].lower()
    if unit not in time_units:
        return None
    
    number = findall(r"(?:\d*\.*\d+)", str_time[:-1])
    if not number:
        return None
    
    return round(float(number[0]) * time_units[unit])

def is_valid_with_pattern(pattern, time_string):
    if match(pattern, time_string):
        return True
    return False

def date_is_less_than_(start_date, end_date):
    if end_date < start_date:
        return True
    return False

if __name__ == "__main__":
    seconds = 1000
    print(convert_to_date(seconds))