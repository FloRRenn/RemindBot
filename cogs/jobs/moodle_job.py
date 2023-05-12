from discord import app_commands, Interaction, Embed
from discord.ext import commands, tasks
import os

from ultils.db_action import Database
from ultils.moddle import Moodle
from ultils.time_convert import convert_to_another_timezone, datetime

class MyMoodle(commands.GroupCog, name = "moodle"):
    CHANNEL_ID = 1058633075166302258
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("moodle")
        self.mention_role = "<@&1018874542132822077>"
        
        self.moodle = Moodle()
        #self.moodle.new_session()
        
        self.moodle_checker.start()
        self.moodle_reminder.start()
        
    @app_commands.command(name = "hack", description = "Lấy acc moodle th Tấn")
    async def _this_week(self, interaction : Interaction):
        response = os.getenv('MOODLE_AUTH_TOKEN')
        await interaction.response.send_message(response)

    
    # @app_commands.command(name = "pingz", description = "Lấy deadline tháng này")
    # async def _this_month(self, interaction : Interaction, user_input : str):
    #     response = os.system("ping -c 1 " + user_input)
    #     await interaction.response.send_message(response)    
    
    @tasks.loop(hours = 3)
    async def moodle_checker(self):
        data = await self.moodle.auto_get_data("monthnow")
        if not data:
            return
        
        channel = self.bot.get_channel(self.CHANNEL_ID)
        for info in data:
            isExisted = self.db.find({"course_id" : info["course_id"]})
            
            if not isExisted:
                timestamp_for_show = convert_to_another_timezone(info["end_time"], "Asia/Ho_Chi_Minh", "Asia/Ho_Chi_Minh")
                embed = Embed(title = info["title"], description = info["description"], color = 0x00ff00)
                embed.add_field(name = "Deadline", value = f"{info['end_time']} <t:{timestamp_for_show}:R>")
                embed.set_author(name = info["class"])
                embed.set_thumbnail(url = "https://tuoitre.uit.edu.vn/wp-content/uploads/2015/07/logo-uit.png")
                
                message = await channel.send(self.mention_role, embed = embed)
                    
                timestamp = convert_to_another_timezone(info["end_time"], "Asia/Ho_Chi_Minh", 'Etc/GMT')
                info["timestamp"] = timestamp
                info["message_id"] = message.id
                self.db.insert(info)
                
    @tasks.loop(minutes = 2)
    async def moodle_reminder(self):
        query = {"type" : "moodle_data"}
        data = self.db.get_all(query)
        documents_count = self.db.count(query)
        
        channel = self.bot.get_channel(self.CHANNEL_ID)
        
        if documents_count != 0:
            timestamp = datetime.now().timestamp()
            
            day = 24 * 60 * 60 + timestamp # seconds
            _12h = 12 * 60 * 60 + timestamp # seconds
            _5m = 5 * 60 + timestamp # seconds
            
            for info in data:
                await self.process_notification(channel, info, day, _12h, _5m)
                
    @moodle_checker.before_loop
    @moodle_reminder.before_loop
    async def before(self):
        await self.bot.wait_until_ready()
                 
    async def process_notification(self, channel, info, day, _12h, _5m):
        content = ''
        
        if day - 120 < info["timestamp"] <= day:
            content = "Còn **1 ngày** nữa là đến deadline. Đừng xàm lông nữa :v."
            
        elif _12h - 120 < info["timestamp"] <= _12h:
            content = "Còn **12 giờ** nữa là đến deadline, tốc độ lên."
            
        elif _5m - 60 < info["timestamp"] <= _5m:
            content = "Còn **5 phút nữa**"
            self.db.remove({"course_id" : info["course_id"]})
            
            
        if content:
            message = await channel.fetch_message(info["message_id"])
            await message.delete()
            
            message = await channel.send(content, embed = message.embeds[0])
            self.db.update(info, {"$set" : {"message_id" : message.id}})
            
async def setup(bot : commands.Bot):
    await bot.add_cog(MyMoodle(bot))