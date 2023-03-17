from discord import app_commands, Interaction, Embed, Member, Colour
from discord.ext import commands, tasks

from typing import Optional

class Server(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name = "server_info", description = "Tạo kênh")
    async def _sv_info(self, interaction : Interaction):
        embed = Embed(title = f"Server {interaction.guild.name}", description = " Thông tin về server", color = Colour.blue())
        embed.add_field(name = '🆔Server ID', value = f"{interaction.guild.id}", inline = True)
        embed.add_field(name = '📆Tạo ngày', value = interaction.guild.created_at.strftime("%b %d %Y"), inline = True)
        embed.add_field(name = '👑Owner', value = f"{interaction.guild.owner}", inline = True)
        embed.add_field(name = '👥Members', value = f'{interaction.guild.member_count} Members', inline = True)
        embed.add_field(name = '💬Channels', value = f'{len(interaction.guild.text_channels)} Text | {len(interaction.guild.voice_channels)} Voice', inline = True)
        await interaction.response.send_message(embed = embed)

    # @app_commands.command(name = "user_status")
    # async def _get_status(self, interaction : Interaction, member : Member):
    #     user = interaction.guild.get_member(member.id)
    #     data = f"raw_status: {user.raw_status}\n" + \
    #             f"status: {user.status}\n" + \
    #             f"web_status: {user.web_status}\n" + \
    #             f"mobile_status: {user.mobile_status}\n" + \
    #             f"desktop_status: {user.desktop_status}" + \
    #             f"activities: {user.st}" 
    #     await interaction.response.send_message(data)

    @app_commands.command(name = "help", description = "Tạo kênh")
    async def _help(self, insteraction : Interaction, search : Optional[str]):
        pass
    
async def setup(bot : commands.Bot):
    await bot.add_cog(Server(bot))