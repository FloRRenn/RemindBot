from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands
from typing import Optional

from ultils.panels import VotePanel, VoteEditPanel, randint
from ultils.db_action import Database

class VoteCMD(commands.GroupCog, name = "vote"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("vote")
        
    @app_commands.command(name = "new_vote", description = "Tạo vote")
    async def _new_vote(self, interaction : Interaction, title : app_commands.Range[str, 3, 50], how_many_votes : app_commands.Range[int, 1, 5], 
                        description : Optional[str] = "", thumbnail : Optional[str] = "",
                        send_to : Optional[TextChannel] = None):
        
        if send_to is None:
            send_to = interaction.channel
            
        id_ = randint(0, 9999)
        vote = VotePanel(id_, how_many_votes, description, send_to, thumbnail, self.db, title = title)
        await interaction.response.send_modal(vote)
        
    @app_commands.command(name = "edit_vote", description = "Chỉnh sửa vote")
    async def _edit_vote(self, interaction : Interaction, vote_id : int, description : Optional[str] = "", thumbnail : Optional[str] = "",):
        data = self.db.find({"vote_id" : vote_id, "user_id" : interaction.user.id})
        if not data:
            return await interaction.response.send_message(f"Không tìm thấy vote có ID {vote_id}", ephemeral = True)
        
        modal = VoteEditPanel(vote_id, data["num_of_vote"], 
                              description, thumbnail, data["votes"],
                              data["channel_id"], data["message_id"], 
                              self.db, 
                              title = "Edit: "+ data["title"])
        await interaction.response.send_modal(modal)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(VoteCMD(bot))