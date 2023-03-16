from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands
from typing import Optional

from ultils.panels import VotePanel, randint

class VoteCMD(commands.GroupCog, name = "vote"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        
    @app_commands.command(name = "new_vote", description = "Tạo vote")
    async def _new_vote(self, interaction : Interaction, title : app_commands.Range[str, 3, 50], how_many_votes : app_commands.Range[int, 1, 5], 
                        description : Optional[str] = "", thumbnail : Optional[str] = "",
                        send_to : Optional[TextChannel] = None):
        
        if send_to is None:
            send_to = interaction.channel
            
        id_ = randint(0, 9999)
        vote = VotePanel(id_, how_many_votes, description, send_to, thumbnail, title = title)
        await interaction.response.send_modal(vote)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(VoteCMD(bot))