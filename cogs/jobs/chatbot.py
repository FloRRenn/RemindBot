from discord import app_commands, Interaction, File, Message
from discord.ext import commands, tasks
from typing import Optional

import os
from dotenv import load_dotenv

from antispam import AntiSpamHandler, Options
from antispam.plugins import AntiSpamTracker
from antispam.caches.mongo import MongoCache
from antispam.enums import Library

from ultils.chatgpt import ChatGPT
from ultils.db_action import Database
from ultils.permission import is_botOwner
from ultils.filter_content import filter

is_not_answering = True
def check_it_is_answering(interaction : Interaction = None):
    global is_not_answering
    return is_not_answering

class ChatBot(commands.GroupCog, name = "chatbot"):
    def __init__(self, bot : commands.Bot):
        self.db = Database("gpt")
        self.bot = bot
        
        # Detect spamming
        self.bot.handler = AntiSpamHandler(self.bot, Library.ENHANCED_DPY, options=Options(no_punish = True,  message_duplicate_count = 2))
        self.bot.tracker = AntiSpamTracker(self.bot.handler, 5)
        self.bot.handler.register_plugin(self.bot.tracker)
        self.bot.handler.set_cache(MongoCache(self.bot.handler, self.load_mongo_uri()))
        
        # Chat bot
        self.chatbot = ChatGPT(self.load_api())
        self.chatbot_2 = ChatGPT(self.load_api())
        self.auto_chat_channel = self.load_auto_chat_channel()
        
    def load_mongo_uri(self):
        return os.getenv("MONGODB_URI")

    def load_api(self):
        data = self.db.find({"type" : "api_key"})
        if not data:
            raise Exception("API key not found")
        return data["api_key"]
    
    def load_auto_chat_channel(self):
        data = self.db.get_all({"type" : "auto_reply", "enable" : 'True'})
        if not data:
            return []
        return [guild["channel_id"] for guild in data]

    @app_commands.command(name = "new_api_key")
    @is_botOwner()
    async def _set_api_key(self, interaction : Interaction, api_key : str):
        await interaction.response.defer(thinking = True)
        global is_not_answering
        data = {
            "api_key" : api_key,
            "type" : "api_key",
            "default_key" : True
        }

        self.db.update({"type" : "api_key"}, {"$set" : data})
        while is_not_answering == False:
            continue
        
        self.chatbot.api_key = api_key
        await interaction.followup.send("Update new API key", ephemeral = True)

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
        
        
    @app_commands.command(name = "auto_answer", description = "Chọn kênh này làm kênh tự động trả lời tin nhắn")
    @app_commands.choices(enable = [
                                    app_commands.Choice(name = "Yes", value = "True"),
                                    app_commands.Choice(name = "No", value = "False"),
                                    ])
    async def _set_auto_chat(self, interaction : Interaction, enable : app_commands.Choice[str]):
        await interaction.response.defer(thinking = True)
        
        channel_id = interaction.channel.id
        data = {
                "type" : "auto_reply",
                "enable" : enable.value,
                "channel_id" : channel_id,
                "guild_id" : interaction.guild.id
            }
            
        self.db.update(
                        {"type" : "auto_reply", "guild_id" : interaction.guild.id}, 
                        {"$set" : data}, 
                        upsert = True
                    )

        if enable.value == True:
            if channel_id not in self.auto_chat_channel:
                self.auto_chat_channel.append(channel_id)
            await interaction.followup.send(f"Đã bật chế độ tự động trả lời tin nhắn tại kênh {interaction.channel.mention}", ephemeral = False)
            
        else:
            if channel_id in self.auto_chat_channel:
                self.auto_chat_channel.remove(channel_id)
                return await interaction.followup.send(f"Đã tắt chế độ tự động trả lời tin nhắn tại kênh {interaction.channel.mention}", ephemeral = False)
            
            return await interaction.followup.send(f"Kênh {interaction.channel.mention} không được bật chế độ tự động trả lời tin nhắn", ephemeral = False)
        
    @commands.Cog.listener()
    async def on_message(self, message : Message):
        if message.author.bot:
            return
        
        if message.channel.id in self.auto_chat_channel:
            content = message.content
            
            await self.bot.handler.propagate(content)
            if not filter(content) or await self.bot.tracker.is_spamming(message):
                return await message.channel.send("Sao giống spam vậy. Muốn đánh nhau không?")
            
            async with message.channel.typing():
                answer = await self.chatbot_2.ask(message.content)
                await message.channel.send(answer)

async def setup(bot : commands.Bot):
    await bot.add_cog(ChatBot(bot))