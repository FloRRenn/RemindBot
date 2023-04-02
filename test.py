import time

local_offset = -time.timezone if (time.localtime().tm_isdst == 0) else -time.altzone
local_offset_hours = local_offset // 3600
local_offset_minutes = (local_offset % 3600) // 60
gmt_offset = f"GMT{'+' if local_offset >= 0 else '-'}{abs(local_offset_hours):02d}:{abs(local_offset_minutes):02d}"

print(gmt_offset)
