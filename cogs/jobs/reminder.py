from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands, tasks
from typing import Optional

from random import randint

from ultils.db_action import Database
from ultils.remind import ManageReminder
from ultils.panels import NewRemind, is_valid_with_pattern, datetime

class Reminder(commands.GroupCog, name = "remind"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("reminder")
        # self.reminders = ManageReminder(self.db)
        # self.check_remind.start()

    # def default_channel(self, guild_id, channel_id):
    #     data = {
    #         "default_channel": channel_id,
    #         "guild_id": guild_id,
    #         "index_num" : 0
    #     }
        
    #     if self.db.find(data) is None:
    #         self.db.insert(data)
    #     else:
    #         self.db.update(data)
        
    # @app_commands.command(name = "set_default_channel", description = "Set a default channel for reminder")
    # async def _set_default_channel(self, interaction : Interaction, channel : TextChannel):
    #     channel_id = channel.id
    #     guild_id = interaction.guild.id
    #     self.default_channel(guild_id, channel_id)
    #     await interaction.response.send_message(f"Đã thiết lập kênh mặc định là {channel.mention}", ephemeral = True)
        
    # @app_commands.command(name = "new_remind", description = "Set a reminder")
    # async def _set_remind(self, interaction : Interaction, content : str, 
    #                   end_date : str, time : Optional[str] = "", start_date : Optional[str] = "", 
    #                   mention_who : Optional[Member] = None):
        
    #     guild_id = interaction.guild.id
    #     if not self.db.find({"guild_id" : guild_id}):
    #         self.default_channel(guild_id, interaction.channel.id)

    #     remind_id = randint(0, 2**16)
    #     user = interaction.user.id
    #     if mention_who is None:
    #         mention_who = 0
    #     else:
    #         mention_who = mention_who.id
            
    #     reminder = Remind(remind_id, user, content, end_date, time, start_date, mention_who, guild_id)
    #     self.reminders.add_remind(reminder)
    #     await interaction.response.send_message(embed = reminder.send_embed(), ephemeral = True)
        
    # @app_commands.command(name = "list_remind", description = "List all reminders")
    # async def _list_remind(self, interaction : Interaction):
    #     await interaction.response.defer()
        
    #     userID = interaction.user.id
    #     list_remind = await self.reminders.get_list_remind_from_user(userID)
        
    #     if list_remind is not None:
    #         for i in list_remind:
    #             await interaction.followup.send(embed = i, ephemeral = True)
    #     else:
    #         await interaction.followup.send(embed = Embed(title = "Reminder", description = "Bạn không bất kỳ lịch nhắc nào", colour = 0x00ff00), ephemeral = True)
            
    # @app_commands.command(name = "delete_remind", description = "Delete a reminder")
    # async def _delete_remind(self, interaction : Interaction, remind_id : int):
    #     userID = interaction.user.id
    #     result = await self.reminders.remove_remind(userID, remind_id)
    #     if result:
    #         await interaction.response.send_message("Đã xóa thành công", ephemeral = True)
    #     else:
    #         await interaction.response.send_message("Không tìm thấy lịch nhắc", ephemeral = True)
            
    # @app_commands.command(name = "edit_remind", description = "Edit a reminder")
    # async def edit_remind(self, interaction : Interaction, remind_id : int, 
    #                       content : Optional[str] = "", 
    #                       end_date : Optional[str] = "", time : Optional[str] = "", start_date : Optional[str] = "", 
    #                       mention_who : Optional[Member] = None):
    #     userID = interaction.user.id
    #     if self.reminders.edit_remind(userID, remind_id, content, end_date, time, start_date, mention_who.id):
    #         await interaction.response.send_message("Đã sửa thành công", ephemeral = True)
    #     else:
    #         await interaction.response.send_message("Không tìm thấy lịch nhắc", ephemeral = True)
            
    # @tasks.loop(seconds = 60)
    # async def check_remind(self):
    #     cache = {}
    #     get_list = await self.reminders.check_list()
        
    #     for i in get_list:
    #         guildID = i[0]
    #         if guildID not in cache:
    #             default_channel_id = self.db.find({"index_num" : 0, "guild_id" : guildID})
    #             channel = self.bot.get_channel(default_channel_id["default_channel"])
    #             cache[guildID] = channel
            
    #         if i[2] != 0:
    #             member = self.bot.get_user(i[2])
    #             await cache[guildID].send(f"{member.mention}", embed = i[1])
    #         else:
    #             await cache[guildID].send(embed = i[1])

    # @check_remind.before_loop
    # async def before_check_remind(self):
    #     await self.bot.wait_until_ready()
    
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
        data = {"remind_id" : remind_id}
        
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
            
        if end_time != "":
            if not is_valid_with_pattern(end_time, "time_pattern"):
                return await interaction.response.send_message("**Thời gian không hợp lệ**", ephemeral = True)
            data["end_time"] = end_time
            
        if mention_who is not None:
            data["mention_id"] = [mention_who.id, interaction.user.id]
            
        result = self.db.update({"user_id" : interaction.user.id, "remind_id" : remind_id}, {"$set" : data})
        if result.modified_count != 0:
            await interaction.response.send_message("**Đã sửa thành công**", ephemeral = True)
        else:
            await interaction.response.send_message(f"**Không tìm thấy lịch nhắc có id {remind_id}**", ephemeral = True)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(Reminder(bot))