import re

time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'

def is_valid_time(time_string):
    if re.match(time_pattern, time_string):
        return True
    else:
        return False


if __name__ == "__main__":
    print(is_valid_time("-12:12"))
