from discord import app_commands, Interaction, Member, TextChannel, Attachment, PartialMessageable
from discord.ext import commands
from typing import Optional
import random

class XamLoz(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name = "gay", description = "Xem chỉ số gay")
    async def _gay(self, interaction : Interaction, user : Optional[Member]):
        if user is None:
            user = interaction.user
        index = random.randint(0, 100)
        await interaction.response.send_message(f"Chỉ số **GAY** của {user.mention} là ||{index}%||" )  

async def setup(bot : commands.Bot):
    await bot.add_cog(XamLoz(bot))

    