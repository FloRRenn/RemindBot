from discord import app_commands, Interaction, File
from discord.ext import commands
from typing import Optional
import os

from ultils.chatgpt import ChatGPT
from ultils.db_action import Database
from ultils.permission import is_botOnwer

class ChatBot(commands.GroupCog, name = "chatbot"):
    def __init__(self, bot : commands.Bot):
        self.db = Database("gpt")
        self.bot = bot
        self.chatbot = ChatGPT(self.load_api())

    def load_api(self):
        data = self.db.find({"type" : "api_key"})
        if not data:
            raise Exception("API key not found")
        return data["api_key"]

    @app_commands.command(name = "new_api_key")
    @is_botOnwer()
    async def _set_api_key(self, interaction : Interaction, api_key : str):
        data = {
            "api_key" : api_key,
            "type" : "api_key"
        }

        self.db.update({"type" : "api_key"}, {"$set" : data})
        await interaction.response.send_message("Update new API key", ephemeral = True)

    @app_commands.command(name = "ask")
    async def _ask(self, interaction : Interaction, *, question : str):
        await interaction.response.defer(thinking = True)

        answer = await self.chatbot.ask(question)

        if len(answer) < 2000:
            return await interaction.followup.send(answer)
        
        filename = f"answer-for-user-{interaction.user.id}.txt"
        with open(filename, "w+", encoding = "utf-8") as f:
            f.write(answer)
        file = File(filename)
        await interaction.followup.send("Bởi vì câu trả lời quá dài nên tôi sẽ gửi chúng dưới dạng file", file = file)

        os.remove()

async def setup(bot : commands.Bot):
    await bot.add_cog(ChatBot(bot))