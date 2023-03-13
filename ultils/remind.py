from datetime import datetime
from discord import Embed

class Remind:
    def __init__(self, remindID, user, content, 
                        end_date, time, start_date, mention_role):
        self.remindID = remindID
        self.owned_user = user
        self.content = content
        self.time = time
        self.end_date = end_date
        self.start_date = start_date
        self.mention_role = mention_role
    
    def get_remindID(self):
        return self.remindID
    
    def get_userID(self):
        return self.user.id
    
    def set_new_time(self, new_time):
        if new_time != "":
            self.time = new_time
    
    def set_new_end_date(self, new_end_date):
        if new_end_date != "":
            self.end_date = new_end_date
        
    def set_new_start_date(self, new_start_date):
        if new_start_date != "":
            self.start_date = new_start_date
    
    def set_new_mention_role(self, new_mention_role):
        if new_mention_role is not None:
            self.mention_role = new_mention_role
    
    def set_new_content(self, new_content):
        if new_content != "":
            self.content = new_content
    
    def send_embed(self):
        embed = Embed(title = "Reminder", description = self.content, colour = 0x00ff00)
        embed.set_author(name = f"Reminder ID: {self.remindID}")
        if self.start_date:
            embed.add_field(name = "Start date", value = self.start_date)
        embed.add_field(name = "End date", value = self.end_date + " " + self.time)
        embed.set_footer(text = f"Reminder created by {self.owned_user}")
        return embed
    
    def to_dict(self):
        return {
            "remindID" : self.remindID,
            "owned_user" : self.owned_user.id,
            "content" : self.content,
            "time" : self.time,
            "end_date" : self.end_date,
            "start_date" : self.start_date,
            "mention_role" : self.mention_role.id
        }
    
class ManageReminder:
    def __init__(self, db):
        self.db = db
        
        self.list_remind = []
        self.load_reminder()
        
    def load_reminder(self):
        data = self.db.get_all()
        for i in data:
            reminder = Remind(
                            i["remindID"], i["owned_user"], i["content"], 
                            i["end_date"], i["time"], i["start_date"], i["mention_role"]
                            )
            self.list_remind.append(reminder)
            
    def add_remind(self, remind):
        self.list_remind.append(remind)
        self.db.insert(remind.to_dict())
        
    def edit_remind(self, userID, remind_id, content, end_date, time, start_date, mention_who):
        for i in self.list_remind:
            if i.get_remindID() == remind_id and i.get_userID() == userID:
                i.set_new_content(content)
                i.set_new_end_date(end_date)
                i.set_new_time(time)
                i.set_new_start_date(start_date)
                i.set_new_mention_role(mention_who)
                self.db.update(i.to_dict())
                return True
        return False
        
    async def remove_remind(self, userID, remindID):
        for i in self.list_remind:
            if i.get_remindID() == remindID and i.get_userID() == userID:
                self.list_remind.remove(i)
                self.db.remove({"remindID" : remindID})
                return True
        return False
    
    async def get_list_remind_from_user(self, userID):
        list_remind = []
        for i in self.list_remind:
            if i.get_userID() == userID:
                list_remind.append(i.send_embed())
        return list_remind
    
    async def check_list(self):
        for i in self.list_remind:
            if i.get_end_date() == datetime.now().strftime("%d/%m/%Y") and i.get_time() >= datetime.now().strftime("%H:%M"):
                self.remove_reminder(i.get_remindID())
                yield i.send_embed()
    
    async def check_remind(self, remindID):
        for i in self.list_remind:
            if i.get_remindID() == remindID:
                return i.send_embed()
        return None
        