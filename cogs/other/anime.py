from discord import app_commands, Interaction, Member
from discord.ext import commands

class Anime(commands.GroupCog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name = "anime", description = "Tìm kiếm thông tin anime")
    async def _anime(self, interaction : Interaction, anime_name : str):
        pass