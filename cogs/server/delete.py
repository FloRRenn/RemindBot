from discord import app_commands, Interaction, Embed, Member, Role
from discord.ext import commands
from typing import Optional, List

from re import findall
import asyncio

class DeleteMessages(commands.GroupCog, name = "delete"):
    def __init__(self, bot):
        self.bot = bot
        
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

    @app_commands.command(name = "messages", description = "Xóa tin nhắn")
    async def _text(self, interaction : Interaction, word : Optional[str] = "",  
                    user : Optional[Member] = None, file : Optional[bool] = False,
                    limit : app_commands.Range[int, 1, 50] = 20):
        await interaction.response.defer()
        word = word.lower()
        
        # 1 : word, 2 : user, 4 : file
        decide_val = 0
        if word != "":
            decide_val += 1
        if user != None:
            decide_val += 2
        if file:
            decide_val += 4
            
        channel = interaction.channel
        count = 0
        async for message in channel.history(limit = limit + 10):
            value = 0
            if word != "" and word in message.content.lower():
                value += 1
            
            if user is not None and user.id == message.author.id:
                value += 2
                
            if file == True and len(message.attachments) != 0:
                value += 4
            
            if value == decide_val:
                await message.delete()
                await asyncio.sleep(0.35)
                count += 1

            if count == limit:
                break
            
        message = await interaction.followup.send(f"Đã xóa **{count}** tin nhắn", ephemeral = True)
        await asyncio.sleep(2)
        await message.delete()
    
async def setup(bot : commands.Bot):
    await bot.add_cog(DeleteMessages(bot))