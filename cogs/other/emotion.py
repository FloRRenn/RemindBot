from discord import app_commands, Interaction, Member, Embed, Attachment
from discord.ext import commands
from typing import Optional
import aiohttp
import re

from ultils.db_action import Database

choices = [
            app_commands.Choice(name = "Hạnh phúc", value = "happy"),
            app_commands.Choice(name = "Tức giận", value = "angry"),
            app_commands.Choice(name = "Buồn", value = "sad"),
            app_commands.Choice(name = "Sợ hãi", value = "fear"),
            app_commands.Choice(name = "Ngạc nhiên", value = "surprise"),
            app_commands.Choice(name = "Thất vọng", value = "disappointed"),
            app_commands.Choice(name = "Yêu", value = "love"),
            app_commands.Choice(name = "Buồn cười", value = "simle"),
            app_commands.Choice(name = "Simp", value = "simp"),
            app_commands.Choice(name = "Kinh bỉ", value = "scorn"),
            app_commands.Choice(name = "Câm", value = "shut_up"),
            app_commands.Choice(name = "Xấu hổ", value = "shy"),
            ]

class Emotion(commands.GroupCog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database("emotion")
        
        self.url_pattern = re.compile(r"^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$")
        self.image_content_type = ["image/png", "image/jpeg", "image/gif", "image/webp", 
                                   "image/jpg", "image/bmp", "image/tiff"]
        
    async def check_link(self, url):
        if (not re.match(self.url_pattern, url)):
            return {
                "status": False,
                "message": "Đây không phải là link"
            }
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "status": False,
                        "message": "Không thể truy cập link"
                    }
                    
                content_type = response.headers.get("content-type")
                if content_type not in self.image_content_type:
                    return {
                        "status": False,
                        "message": "Link không trỏ tới ảnh"
                    }

                return {
                    "status": True,
                    "message": "ok"
                }

    @app_commands.command(name = "send_image", description = "Truyền tải cảm xúc bằng ảnh")
    @app_commands.choices(choice = choices)
    async def _send_image(self, interaction : Interaction, choice : app_commands.Choice[str],
                          message : Optional[str] = "", mention_who : Optional[Member] = None):
        image = self.db.get_random({"type": choice.value})
        text = " "
        if mention_who:
            text = f"{mention_who.mention} "
        text += f"{message} "
        
        embed = Embed(color = 0x00ff00)
        embed.set_image(url = image["link"])
        await interaction.response.send_message(text, embed = embed, ephemeral = False)
        
    @app_commands.command(name = "add_image_from_url", description = "Thêm ảnh vào cơ sở dữ liệu")
    @app_commands.choices(choice = choices)
    async def _add_image(self, interaction : Interaction, choice : app_commands.Choice[str], link : str):
        check = await self.check_link(link)
        if check["status"]:
            self.db.insert({"type": choice.value, "link": link})
            await interaction.response.send_message("Đã thêm ảnh vào cơ sở dữ liệu", ephemeral = True)
        else:
            await interaction.response.send_message(check["message"], ephemeral = True)
            
    @app_commands.command(name = "add_image_from_attachment", description = "Thêm ảnh vào cơ sở dữ liệu")
    @app_commands.choices(choice = choices)
    async def _add_image_from_attachment(self, interaction : Interaction, choice : app_commands.Choice[str], file : Attachment):
        check = await self.check_link(file.url)
        if check["status"]:
            self.db.insert({"type": choice.value, "link": file.url})
            await interaction.response.send_message("Đã thêm ảnh vào cơ sở dữ liệu", ephemeral = True)
        else:
            await interaction.response.send_message(check["message"], ephemeral = True)
    
async def setup(bot : commands.Bot):
    await bot.add_cog(Emotion(bot))