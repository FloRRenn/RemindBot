from discord import app_commands, Interaction, TextChannel, Embed
from discord.ext import commands
from typing import Optional

from ultils.panels import ToDoPanel, ToDoPanelEdit
from ultils.db_action import Database

class todojob(commands.GroupCog, name = "todo"):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.db = Database("todo")
        
    @app_commands.command(name = "create", description = "Lập một công việc mới")
    async def _create(self, interaction : Interaction, send_to : Optional[TextChannel] = None) -> None: 
        panel = ToDoPanel(send_to, self.db)
        await interaction.response.send_modal(panel)
        
    @app_commands.command(name = "edit", description = "Chỉnh sửa công việc")
    async def _edit(self, interaction : Interaction, todo_id : int, send_to : Optional[TextChannel] = None) -> None:
        data = self.db.find({"todo_id" : todo_id, "user_id": interaction.user.id})
        if not data:
            return await interaction.response.send_message(f"Không tìm thấy công việc có id {todo_id}", ephemeral = True)
        
        title = f"Chỉnh sửa công việc {todo_id}"
        panel = ToDoPanelEdit(todo_id, title, data["title"], data["todo_list"], send_to, self.db)
        await interaction.response.send_modal(panel)
        
    @app_commands.command(name = "delete", description = "Xóa công việc")
    async def _delete(self, interaction : Interaction, todo_id : int) -> None:
        data = self.db.find({"todo_id" : todo_id, "user_id": interaction.user.id})
        if not data:
            return await interaction.response.send_message(f"Không tìm thấy công việc có id {todo_id}", ephemeral = True)
        
        self.db.remove({"todo_id" : todo_id, "user_id": interaction.user.id})
        await interaction.response.send_message(f"Đã xóa công việc {todo_id}", ephemeral = True)
        
    @app_commands.command(name = "list", description = "Xem danh sách công việc")
    async def _list(self, interaction : Interaction) -> None:
        await interaction.response.defer(ephemeral = True)
        
        data = self.db.get_all({"user_id": interaction.user.id})
        check = False
        
        for i in data:
            embed = Embed(title = i["title"], description = i["todo_list"], color = 0x00ff00)
            embed.set_author(name = f"ID: {i['todo_id']}")
            embed.set_footer(text = f"Người tạo: {interaction.user.name}#{interaction.user.discriminator}")
            await interaction.followup.send(embed = embed, ephemeral = True)
            check = True
        
        if not check:
            await interaction.followup.send("Bạn chưa có công việc nào", ephemeral = True)
            
async def setup(bot : commands.Bot):
    await bot.add_cog(todojob(bot))