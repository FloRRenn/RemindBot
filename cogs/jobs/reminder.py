from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands
from typing import Optional

from ultils.db_action import Database
from ultils.remind import ManageReminder, Remind

class Reminder(commands.GroupCog, name = "remind"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("reminders")
        self.reminders = ManageReminder(self.db)
        
    @app_commands.command(name = "remind", description = "Set a default channel for reminder")
    async def _set_default_channel(self, interaction : Interaction, channel : TextChannel):
        data = {
            "default_channel": channel.id,
        }
        
        if self.db.find(data) is None:
            self.db.insert(data)
        else:
            self.db.update(data)
        
        await interaction.response.send_message(f"Đã thiết lập kênh mặc định là {channel.mention}", ephemeral = True)
        
    @app_commands.command(name = "new_remind", description = "Set a reminder")
    async def _set_remind(self, interaction : Interaction, content : str, 
                      end_date : str, time : Optional[str] = "", start_date : Optional[str] = "", 
                      mention_who : Optional[Member] = None):
        
        reminder = Remind(content, end_date, time, start_date, mention_who)
        self.reminders.add_remind(reminder)
        await interaction.response.send_message(embed = reminder.send_embed(), ephemeral = True)
        