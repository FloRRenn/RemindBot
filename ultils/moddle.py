import aiohttp
import os
from icalendar import Calendar, Event

class Moodle:
    def __init__(self):
        self.url = f"https://courses.uit.edu.vn/calendar/export_execute.php?userid={os.getenv('MOODLE_ID')}&authtoken={os.getenv('MOODLE_AUTH_TOKEN')}&preset_what=courses&preset_time="
        self.session = None
        
        self.header = {
            'Cookie': f'_ga=GA1.3.510450955.1651059609; MoodleSession={os.getenv("MOODLE_SESSION")}; MOODLEID1_={os.getenv("MOODLE_ID1")}',
            'Referer': 'https://courses.uit.edu.vn/calendar/export.php',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        
    def new_session(self):
        self.session = aiohttp.ClientSession(headers = self.header)
        
    def close_session(self):
        self.session.close()
        self.session = None
        
    async def get_data(self, preset_time):
        # weeknow
        # monthnow
        # recentupcoming
        # custom
        async with self.session.get(self.url + preset_time) as resp:
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
    moddle = Moodle()
    
    import requests
    header = {
        'Cookie': '_ga=GA1.3.510450955.1651059609; MoodleSession=k479v2kvpum21sfjltcsgdk6ks; MOODLEID1_=%25FF%25FF%250E%250B%258A%25A5%25D4%25BF',
        'Referer': 'https://courses.uit.edu.vn/calendar/export.php',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    resp = requests.get(moddle.url + "weeknow", headers = header)
    print(resp.content)