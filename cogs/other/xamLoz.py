from discord import app_commands, Interaction, Member, TextChannel, Attachment, PartialMessageable
from discord.ext import commands
from typing import Optional
import random, asyncio

class XamLoz(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name = "gay", description = "Xem chỉ số gay")
    async def _gay(self, interaction : Interaction, user : Optional[Member]):
        if user is None:
            user = interaction.user
        index = random.randint(0, 100)
        await interaction.response.send_message(f"Chỉ số **GAY** của {user.mention} là ||{index}%||")  
        
    @app_commands.command(name = "spam", description = "Spam message")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def _spam(self, interaction : Interaction, user : Member, message : str, limit : app_commands.Range[int, 1, 15] = 7):
        await interaction.response.defer(ephemeral = True)
        
        for _ in range(limit):
            await user.send(f"From {interaction.user.name}: " + message)
            await asyncio.sleep(0.5)
        #await interaction.response.send_message(f"Chỉ")     
        await interaction.followup.send("Done!")
        

async def setup(bot : commands.Bot):
    await bot.add_cog(XamLoz(bot))

    