from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands, tasks
from typing import Optional

from ultils.db_action import Database
from ultils.panels import NewRemind, is_valid_with_pattern, datetime, convert_to_timestamp

class Reminder(commands.GroupCog, name = "remind"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("reminder")
        self.guild_cache = self.load_default_channels()
        self.remind_checker.start()
    
    def load_default_channels(self):
        res = {}
        data = self.db.get_all({"type" : "default_channel"})
        for guild in data:
            res[guild["guild_id"]] = guild["default_channel"]
        return res
    
    @app_commands.command(name = "set_default_channel", description = "Chọn kênh mặc định để gửi lịch nhắc")
    @commands.has_permissions(administrator = True)
    async def _set_default_channel(self, interaction : Interaction, channel : TextChannel):
        channelID = channel.id
        guildID = interaction.guild.id
        data = {
            "default_channel": channelID,
            "guild_id": guildID,
            "type" : "default_channel"
        }
        self.db.update({"guild_id" : guildID}, {"$set" : data}, upsert = True)
        self.guild_cache[guildID] = channelID
        await interaction.response.send_message(f"Đã thiết lập kênh mặc định là {channel.mention}", ephemeral = True)
        
    @app_commands.command(name = "new", description = "Tạo nhắc nhở mới")
    async def _set_remind(self, interaction : Interaction, mention_who : Optional[Member] = None):
        mention_id = [interaction.user.id]
        if mention_who:
            mention_id.append(mention_who.id)
            
        modal = NewRemind(mention_who)
        await interaction.response.send_modal(modal)
        
    @app_commands.command(name = "get_remind_id", description = "Lấy lịch nhắc từ ID")
    async def _get_remind_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999]):
        remind = self.db.find({"remind_id" : remind_id, "user_id" : interaction.user.id})
        if remind:
            embed = Embed(title = remind["title"], description = remind["content"], color = 0x00ff00)
            embed.add_field(name = "Ngày nhắc nhở", value = remind["end_date"] + " " + remind["end_time"] + f"\n<t:{remind['timestamp']}:R>")
            embed.set_author(name = f"Remind ID: {remind['remind_id']}")
            
            user = ""
            for user_id in remind["mention_id"]:
                user += f"<@{user_id}> "
            embed.add_field(name = "Người được nhắc", value = user)
            
            await interaction.response.send_message(embed = embed, ephemeral = True)
        
        else:
            await interaction.response.send_message(f"Không tìm thấy lịch nhắc có ID {remind_id}", ephemeral = True)
        
    @app_commands.command(name = "list_remind", description = "Xem danh sách lịch nhắc của bạn")
    async def _list_remind(self, interaction : Interaction):
        query = { "user_id" : interaction.user.id}
        list_reminds = self.db.get_all(query)
        
        remind_to_text = ""
        for remind in list_reminds:
            remind_to_text += f"**➡️ ID: {remind['remind_id']} - {remind['title']} - Ngày nhắc: {remind['end_date']} {remind['end_time']}** (<t:{remind['timestamp']}:R>)\n"
        
        if remind_to_text != "":   
            embed = Embed(title = "Danh sách lịch nhắc bạn", description = remind_to_text, colour = 0x00ff00)
            return await interaction.response.send_message(embed = embed, ephemeral = True)
        
        await interaction.response.send_message("**Bạn không có lịch nhắc nào**", ephemeral = True)
        
    @app_commands.command(name = "delete_from_id", description = "Xóa lịch nhắc của bạn")
    async def _delete_from_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999]):
        query = { "user_id" : interaction.user.id, "remind_id" : remind_id}
        result = self.db.remove(query)
        
        if result.deleted_count != 0:
            await interaction.response.send_message("**Đã xóa thành công**", ephemeral = True)
        else:
            await interaction.response.send_message("**Không tìm thấy lịch nhắc**", ephemeral = True)
            
    @app_commands.command(name = "edit_from_id", description = "Sửa lịch nhắc của bạn")
    async def _edit_from_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999],
                            title : Optional[str] = "", content : Optional[str] = "", 
                            end_date : Optional[str] = "", end_time : Optional[str] = "",
                            mention_who : Optional[Member] = None):
        
        
        data = {"remind_id" : remind_id, "user_id" : interaction.user.id}
        remind_data = self.db.find(data)
        if not remind_data:
            return await interaction.response.send_message(f"**Không tìm thấy lịch nhắc có id {remind_id}**", ephemeral = True)
        
        if title != "":
            data["title"] = title
            
        if content != "":
            data["content"] = content
            
        if end_date != "":
            end_date_ = datetime.strptime(end_date, "%d/%m/%Y").date()
            now = datetime.now().date()
            if not is_valid_with_pattern(end_date, "date_pattern") or end_date_ < now:
                return await interaction.response.send_message("**Ngày không hợp lệ**", ephemeral = True)
            data["end_date"] = end_date
        else:
            data["end_date"] = remind_data["end_date"]
            
        if end_time != "":
            if not is_valid_with_pattern(end_time, "time_pattern"):
                return await interaction.response.send_message("**Thời gian không hợp lệ**", ephemeral = True)
            data["end_time"] = end_time
        else:
            data["end_time"] = remind_data["end_time"]
            
        if mention_who is not None:
            data["mention_id"] = [mention_who.id, interaction.user.id]
        
        data["timestamp"] = convert_to_timestamp(data["end_date"] + " " + data["end_time"], "%d/%m/%Y %H:%M")
        
        self.db.update({"user_id" : interaction.user.id, "remind_id" : remind_id}, {"$set" : data})
        self.update_timestamp(remind_id, data["timestamp"])
        await interaction.response.send_message("**Đã sửa thành công**", ephemeral = True)
        
    @tasks.loop(minutes = 2)
    async def remind_checker(self):
        query = {"type" : "reminder"}
        reminds_list = self.db.get_all(query)
        documents_count = self.db.count(query)
        
        if documents_count != 0:
            alignment = 120 // documents_count
            timestmap = datetime.now().timestamp()
            
            for remind in reminds_list:
                if timestmap >= remind["timestamp"]:
                    self.db.remove({"remind_id" : remind["remind_id"], "user_id" : remind["user_id"]})
                    
                    user = ""
                    for user_id in remind["mention_id"]:
                        user += f"<@{user_id}> "
                    
                    embed = Embed(title = remind["title"], description = remind["content"], color = 0x00ff00)
                    embed.set_footer(text = f"Remind ID: {remind['remind_id']}")
                    
                    await self.bot.get_channel(self.guild_cache[remind["guild_id"]]).send(user, embed = embed)
                timestmap += alignment
                
    @remind_checker.before_loop
    async def before_remind_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot : commands.Bot):
    await bot.add_cog(Reminder(bot))