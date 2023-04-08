import aiohttp
import os
from icalendar import Calendar, Event

class Moodle:
    def __init__(self):
        self.url = f"https://courses.uit.edu.vn/calendar/export_execute.php?userid={os.getenv('MOODLE_ID')}&authtoken={os.getenv('MOODLE_AUTH_TOKEN')}&preset_what=all&preset_time="
        #self.session = None
        
    # def new_session(self):
    #     self.session = aiohttp.ClientSession()
        
    # def close_session(self):
    #     self.session.close()
    #     self.session = None
    
    # weeknow
    # monthnow
    # recentupcoming
    # custom
    async def get_data(self, preset_time):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + preset_time) as resp:
                return await resp.text(encoding = "utf-8")
        
    def parse_data(self, raw_data):
        data = Calendar.from_ical(raw_data)
        res = []

        for component in data.walk():
            if isinstance(component, Event):
                try:
                    info = {
                        "type" : "moodle_data",
                        "course_id" : component.get('UID').split('@')[0],
                        "class" : component.get('CATEGORIES').cats[0],
                        "title" : component.get('SUMMARY'),
                        "description" : component.get('DESCRIPTION'),
                        "end_time" : component.get('DTEND').dt.strftime('%d/%m/%Y %H:%M'),
                    }
                    res.append(info)
                except Exception as e:
                    print(e)
                    print("Error: ", component)         
        return res
    
    async def auto_get_data(self, preset_time):
        raw_data = await self.get_data(preset_time)
        return self.parse_data(raw_data)
        
if __name__ == "__main__":
    import asyncio
    moodle = Moodle()
    #print(moodle.url)
    asyncio.run(moodle.auto_get_data("recentupcoming"))