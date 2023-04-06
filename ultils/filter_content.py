import re
import math

THRESHOLD_ENTROPY = 3.5

def filter(content : str):
    content = content.strip()
    
    if not content:
        return False
    
    # is number
    if re.match('^[0-9\.\ ]*$', content):
        return False
    
    if random_string_detect(content):
        return False
    
    return True
    
def random_string_detect(content : str):
    # Base on Shannon entropy 
    entropy = -sum(prob * math.log2(prob) for prob in (content.count(char) / len(content) for char in set(content)))
    return entropy < THRESHOLD_ENTROPY
    