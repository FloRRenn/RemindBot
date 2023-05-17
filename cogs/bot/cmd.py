from discord import app_commands
from discord.ext import commands
from discord import Interaction

# Error Type
from discord.ext.commands import ExtensionNotLoaded, ExtensionNotFound,\
                                ExtensionAlreadyLoaded, ExtensionFailed
                                
from ultils.permission import is_botOwner

class ManangeCOG(commands.GroupCog, name = "cog"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name = "load", description = "Load Cog's name")
    @is_botOwner()
    async def _load_cog(self, interaction : Interaction, name : str):
        await interaction.response.send_message(f"Loading cog **{name}**...", empheral = True)
        try:
            await self.bot.load_extension(name)
            
        except ExtensionNotFound:
            await interaction.edit_original_response(content = f"Loading cog **{name}**... _DONE_", empheral = True)
            
        except ExtensionAlreadyLoaded:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**LOAD THẤT BẠI:** `Cog đã được load trước đó.`", empheral = True)
            
        except ExtensionFailed:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**LOAD THẤT BẠI:** `Xảy ra lỗi khi load. Xem log để biết thêm chi tiết.`", empheral = True)
        
    @app_commands.command(name = "reload", description = "Reload Cog's name")
    @is_botOwner()
    async def _reload_cog(self, interaction : Interaction, name : str):
        await interaction.response.send_message(f"Reloading cog **{name}**...")
        try:
            await self.bot.reload_extension(name)
            await interaction.edit_original_response(content = f"Reloading cog **{name}**... _DONE_", empheral = True)
            
        except ExtensionNotFound:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**RELOAD THẤT BẠI:** `Không tìm thấy Cog`", empheral = True)
            
        except ExtensionNotLoaded:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**RELOAD THẤT BẠI:** `Không thể load Cog này`", empheral = True)
            
    @app_commands.command(name = "stop", description = "Stop Cog's name")
    @is_botOwner()
    async def _disable_cog(self, interaction : Interaction, name : str):
        await interaction.response.send_message(f"Stopping cog **{name}**...")
        
        try:
            await self.bot.unload_extension(name)
            await interaction.edit_original_response(content = f"Stopping cog **{name}**... _DONE_", empheral = True)
        
        except ExtensionNotFound:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**DỪNG THẤT BẠI:** `Không tìm thấy Cog`", empheral = True)
            
        except ExtensionNotLoaded:
            await interaction.edit_original_response(content = f"Cog **{name}**... \n**DỪNG THẤT BẠI:** `Không thể load Cog này`", empheral = True)
            
class ManangeCMD(commands.GroupCog, name = "cmd"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    async def cmd_config(self, cmd_name : str, type : bool, interaction : Interaction):
        message_type = {
            True : "Enable",
            False : "Disable"
        }
        command = self.bot.get_command(cmd_name)
        if command is None:
            await interaction.response.send_message(f"Không tìm thấy lệnh **{cmd_name}**")
            return

        command.update(enabled = type)
        await interaction.response.send_message(f"{message_type[type]} **{cmd_name}**")
    
    @app_commands.command(name = "enable", description = "Enable command's name")
    @is_botOwner()
    async def _enable(self, interaction : Interaction, name : str):
        await self.cmd_config(name, "Enable", interaction)
    
    @app_commands.command(name = "disable", description = "Disable command's name")
    @is_botOwner()
    async def _disable(self, interaction : Interaction, name : str):
        await self.cmd_config(name, "Disable", interaction)
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ManangeCOG(bot))   
    await bot.add_cog(ManangeCMD(bot))