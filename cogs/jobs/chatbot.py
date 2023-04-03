from discord import app_commands, Interaction, File
from discord.ext import commands, tasks
from typing import Optional
import os

from ultils.chatgpt import ChatGPT
from ultils.db_action import Database
from ultils.permission import is_botOwner

is_not_answering = True
def check_it_is_answering(interaction : Interaction = None):
    global is_not_answering
    return is_not_answering

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
    @is_botOwner()
    async def _set_api_key(self, interaction : Interaction, api_key : str):
        data = {
            "api_key" : api_key,
            "type" : "api_key",
            "default_key" : True
        }

        self.db.update({"type" : "api_key"}, {"$set" : data})
        await interaction.response.send_message("Update new API key", ephemeral = True)

    @app_commands.command(name = "ask", description = "Đặt câu hỏi và bot sẽ trả lời")
    @app_commands.check(check_it_is_answering)
    async def _ask(self, interaction : Interaction, *, question : str):
        global is_not_answering
        is_not_answering = False

        await interaction.response.defer(thinking = True)

        answer = await self.chatbot.ask(question)

        is_not_answering = True
        if len(answer) < 2000:
            return await interaction.followup.send(answer)
        
        filename = f"answer-for-user-{interaction.user.id}.txt"
        with open(filename, "w+", encoding = "utf-8") as f:
            f.write(answer)
        file = File(filename)
        
        await interaction.followup.send("**Bởi vì câu trả lời quá dài nên tôi sẽ gửi chúng dưới dạng file**", file = file)

        os.remove(filename)
        
    @app_commands.command(name = "save_current_chat", description = "Lưu lại cuộc trò chuyện hiện tại")
    @app_commands.check(check_it_is_answering)
    async def _save_current_chat(self, interaction : Interaction):
        filename = f"chat-with-user-{interaction.user.id}.md"
        res = self.chatbot.save_chat(filename)
        if not res:
            return await interaction.response.send_message("Không có cuộc trò chuyện nào để lưu", ephemeral = True)

        file = File(filename)        
        await interaction.response.send_message("**Đây là cuộc trò chuyện hiện tại của bạn**", file = file)
        file.close()
        os.remove(filename)

    @app_commands.command(name = "reset_chat", description = "Xóa thông tin về cuộc trò chuyện cũ")
    @app_commands.check(check_it_is_answering)
    async def _reset_chat(self, interaction : Interaction):
        self.chatbot.reset()
        await interaction.response.send_message("Đã reset thành công")

    @_set_api_key.error
    async def say_error(self, interaction : Interaction, error):
        await interaction.response.send_message("Chỉ có bot owner mới được phép sử dụng lệnh này")

    @_reset_chat.error
    @_ask.error
    @_save_current_chat.error
    async def wait_for_next_chat(self, interaction : Interaction, error):
        await interaction.followup.send("Bot hiện tại đang trả lời câu hỏi của user. Vui lòng thực hiện lại sau khi bot đã trả lời xong.", ephemeral = True)
        
    @tasks.loop(hours = 1)
    async def _auto_reset_chat(self):
        if not check_it_is_answering():
            self.chatbot.reset()
            
    @_auto_reset_chat.before_loop
    async def before_reset_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot : commands.Bot):
    await bot.add_cog(ChatBot(bot))