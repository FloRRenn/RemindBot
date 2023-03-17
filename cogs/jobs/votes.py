from discord import app_commands, Interaction, Member, TextChannel, Embed
from discord.ext import commands
from typing import Optional

from ultils.panels import VotePanel, VoteEditPanel, randint
from ultils.db_action import Database

class VoteCMD(commands.GroupCog, name = "vote"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("vote")
        
    @app_commands.command(name = "create", description = "Tạo vote")
    async def _new_vote(self, interaction : Interaction, title : app_commands.Range[str, 3, 50], how_many_votes : app_commands.Range[int, 1, 5], 
                        description : Optional[str] = "", thumbnail : Optional[str] = "",
                        send_to : Optional[TextChannel] = None):
        
        if send_to is None:
            send_to = interaction.channel
            
        id_ = randint(0, 9999)
        vote = VotePanel(id_, how_many_votes, description, send_to, thumbnail, self.db, title = title)
        await interaction.response.send_modal(vote)
        
    @app_commands.command(name = "edit", description = "Chỉnh sửa vote")
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
        
    @app_commands.command(name = "delete", description = "Xóa vote")
    async def _delete_vote(self, interaction : Interaction, vote_id : int):
        data = self.db.find({"vote_id" : vote_id, "user_id" : interaction.user.id})
        if not data:
            return await interaction.response.send_message(f"Không tìm thấy vote có ID {vote_id}", ephemeral = True)
        
        try:
            self.db.remove({"vote" : vote_id, "user_id" : interaction.user.id})
            channel = self.bot.get_channel(data["channel_id"])
            message = await channel.fetch_message(data["message_id"])
            await message.delete()
            
            await interaction.response.send_message(f"Đã xóa vote có ID {vote_id}", ephemeral = True)
            
        except Exception:
            await interaction.response.send_message(f"Không thể xóa vote có ID {vote_id}, có thể vote đã bị xóa từ trước.", ephemeral = True)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(VoteCMD(bot))