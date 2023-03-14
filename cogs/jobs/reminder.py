from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands, tasks
from typing import Optional

from random import randint

from ultils.db_action import Database
from ultils.remind import ManageReminder, Remind

class Reminder(commands.GroupCog, name = "remind"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("reminder")
        self.reminders = ManageReminder(self.db)

    def default_channel(self, guild_id, channel_id):
        data = {
            "default_channel": channel_id,
            "guild_id": guild_id,
            "index_num" : 0
        }
        
        if self.db.find(data) is None:
            self.db.insert(data)
        else:
            self.db.update(data)
        
    @app_commands.command(name = "set_default_channel", description = "Set a default channel for reminder")
    async def _set_default_channel(self, interaction : Interaction, channel : TextChannel):
        channel_id = channel.id
        guild_id = interaction.guild.id
        self.default_channel(guild_id, channel_id)
        await interaction.response.send_message(f"Đã thiết lập kênh mặc định là {channel.mention}", ephemeral = True)
        
    @app_commands.command(name = "new_remind", description = "Set a reminder")
    async def _set_remind(self, interaction : Interaction, content : str, 
                      end_date : str, time : Optional[str] = "", start_date : Optional[str] = "", 
                      mention_who : Optional[Member] = None):
        
        if not self.db.find({"guild_id" : interaction.guild.id}):
            self.default_channel(interaction.guild.id, interaction.channel.id)

        remind_id = randint(0, 2**16)
        user = interaction.user.id
        reminder = Remind(remind_id, user, content, end_date, time, start_date, mention_who.id, guild_id)
        self.reminders.add_remind(reminder)
        await interaction.response.send_message(embed = reminder.send_embed(), ephemeral = True)
        
    @app_commands.command(name = "list_remind", description = "List all reminders")
    async def _list_remind(self, interaction : Interaction):
        await interaction.response.defer()
        
        userID = interaction.user.id
        list_remind = await self.reminders.get_list_remind_from_user(userID)
        
        if list_remind is not None:
            for i in list_remind:
                await interaction.followup.send(embed = i, ephemeral = True)
        else:
            await interaction.followup.send(embed = Embed(title = "Reminder", description = "Bạn không bất kỳ lịch nhắc nào", colour = 0x00ff00), ephemeral = True)
            
    @app_commands.command(name = "delete_remind", description = "Delete a reminder")
    async def _delete_remind(self, interaction : Interaction, remind_id : int):
        userID = interaction.user.id
        result = await self.reminders.remove_remind(userID, remind_id)
        if result:
            await interaction.response.send_message("Đã xóa thành công", ephemeral = True)
        else:
            await interaction.response.send_message("Không tìm thấy lịch nhắc", ephemeral = True)
            
    @app_commands.command(name = "edit_remind", description = "Edit a reminder")
    async def edit_remind(self, interaction : Interaction, remind_id : int, 
                          content : Optional[str] = "", 
                          end_date : Optional[str] = "", time : Optional[str] = "", start_date : Optional[str] = "", 
                          mention_who : Optional[Member] = None):
        userID = interaction.user.id
        if self.reminders.edit_remind(userID, remind_id, content, end_date, time, start_date, mention_who.id):
            await interaction.response.send_message("Đã sửa thành công", ephemeral = True)
        else:
            await interaction.response.send_message("Không tìm thấy lịch nhắc", ephemeral = True)
            
    @tasks.loop(seconds = 60)
    async def check_remind(self):
        cache = {}
        async for i in await self.reminders.check_list():
            guildID = i[0]
            if guildID not in cache:
                default_channel_id = self.db.find({"index_num" : 0, "guild_id" : guildID})
                channel = self.bot.get_channel(default_channel_id)
                cache[guildID] = channel

            await cache[guildID].send(embed = i[1])

async def setup(bot : commands.Bot):
    await bot.add_cog(Reminder(bot))