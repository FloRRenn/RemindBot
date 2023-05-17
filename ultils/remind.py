from discord import Embed

class Remind:
    def __init__(self, remindID, user, content, 
                        end_date, time, start_date, mention_role, guildID):
        self.remindID = remindID
        self.owned_user = user
        self.content = content
        self.time = time
        self.end_date = end_date
        self.start_date = start_date
        self.mention_role = mention_role
        self.guildID = guildID
    
    def get_remindID(self):
        return self.remindID
    
    def get_userID(self):
        return self.owned_user
    
    def get_mention(self):
        if self.mention_role:
            return self.mention_role
        return 0
    
    def get_guildID(self):
        return self.guildID
    
    def get_end_date(self):
        return self.end_date
    
    def get_time(self):
        return self.time
    
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
            "index_num" : 1,
            "guildID" : self.get_guildID(),
            "remindID" : self.remindID,
            "owned_user" : self.owned_user,
            "content" : self.content,
            "time" : self.time,
            "end_date" : self.end_date,
            "start_date" : self.start_date,
            "mention_role" : self.get_mention()
        }
    
class ManageReminder:
    def __init__(self, db):
        self.db = db
        
        self.list_remind = []
        self.load_reminder()
        
    def load_reminder(self):
        data = self.db.get_all({"index_num" : 1})
        if data:
            for i in data:
                reminder = Remind(
                                i["remindID"], i["owned_user"], i["content"], 
                                i["end_date"], i["time"], i["start_date"], i["mention_role"],
                                i["guildID"]
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
                self.db.update({"remindID" : remind_id} , {"$set" : i.to_dict()})
                return True
        return False
        
    async def remove_remind(self, userID, remindID, index = -1):
        if index != -1:
            self.list_remind.pop(index)
            self.db.remove({"remindID" : remindID})
            return True
        
        index = 0
        for i in self.list_remind:
            if i.get_remindID() == remindID and i.get_userID() == userID:
                self.list_remind.pop(index)
                self.db.remove({"remindID" : remindID})
                return True
            index += 1
        return False
    
    async def get_list_remind_from_user(self, userID):
        list_remind = []
        for i in self.list_remind:
            if i.get_userID() == userID:
                list_remind.append(i.send_embed())
        return list_remind
    
    async def check_list(self):
        return []
        # index = 0
        # notify = []
        
        # for i in self.list_remind:
        #     if i.get_end_date() == datetime.now().strftime("%d/%m/%Y") and i.get_time() >= datetime.now().strftime("%H:%M"):
        #         self.remove_remind(-1, i.get_remindID(), index)
        #         notify.append(i.get_guildID(), i.send_embed(), i.get_mention())
        #     index += 1
            
        # return notify
    
    def check_remind(self, remindID):
        for i in self.list_remind:
            if i.get_remindID() == remindID:
                return i.send_embed()
        return None
        