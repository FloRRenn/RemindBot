from discord import app_commands, Interaction, Embed, Member, Role
from discord.ext import commands
from typing import Optional, List

from re import findall

class DeleteMessages(commands.GroupCog, name = "delete"):
    def __init__(self, bot):
        self.bot = bot
        
    async def link_autocomplete(self, interaction: Interaction, current: bool,
                                ) -> List[app_commands.Choice[str]]:
        choices = ["True", "False"]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]
        
    def has_word(self, message, word):
        return word in message
    
    def has_link(self, message):
        check = findall(r'(https?://[^\s]+)', message)
        if check:
            return True
        return False
    
    def has_file(self, message):
        return len(message.attachments) != 0
    
    def from_user(self, message, user):
        return message.author.id == user.id

    def check(self, message):

    @app_commands.command(name = "messages", description = "Xóa tin nhắn")
    async def _msg(self, interaction : Interaction,
                          word : Optional[str] = None, link : Optional[bool] = None, 
                          file : Optional[bool] = None, user : Optional[Member] = None,
                          limit : int = 50):
        check_value = {
            1 : word,
            2 : link,
            4 : user,
            8 : file
        }
        value_for_delete = 0
        for k, v in check_value.items():
            if v is not None:
                value_for_delete += k
        
        
        channel = interaction.channel
        #async for message in channel.history(limit = limit):
        await interaction.response.send_message("GG")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(DeleteMessages(bot))