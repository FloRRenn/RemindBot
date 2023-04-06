import re

content = "1214 12.15.135 rer"
print(re.match('^[0-9\.\ ]*$', content))