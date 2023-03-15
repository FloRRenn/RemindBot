from discord import Interaction
from discord.ext import commands
from discord.app_commands import AppCommandError

class OnError(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        # logging.debug(error.__class__.__name__)
        await interaction.response.send_message(f"Xảy ra lỗi (**{error.__class__.__name__}**)")
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnError(bot))