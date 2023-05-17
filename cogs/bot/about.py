from discord import app_commands
from discord.ext import commands
from discord import Interaction, Embed

from time import time
from ultils.time_convert import convert_to_date

class AboutBot(commands.GroupCog, name = "bot"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.start_time = time()
        
    def get_latency(self, interaction : Interaction):
        latency = interaction.client.latency
        return round(latency * 1000, 2)
        
    @app_commands.command(name = "ping", description = "Ping to Bot")
    async def _ping(self, interaction : Interaction):
        latency = self.get_latency(interaction)
        await interaction.response.send_message(f"Tôi đây!!\n **Ping: {latency} ms**")
        
    @app_commands.command(name = "uptime", description = "Xem thời gian Uptime")
    async def _uptime(self, ineration : Interaction):
        uptime_date = convert_to_date(time() - self.start_time)
        await ineration.response.send_message(f"Tôi đã hoạt động được: `{uptime_date}`")
        
    @app_commands.command(name = "about", description = "Thông tin về bot")
    async def _about(self, interaction : Interaction):
        latency = self.get_latency(interaction)
        uptime = time() - self.start_time
        
        show = Embed(title = "About me", colour = 0x0FDD62)
        show.add_field(name = "Owner", value = "`HiHi#5793`")
        show.add_field(name = "Ngày sinh", value = "`15/01/2023`")
        show.add_field(name = "Ping", value = f"`{latency} ms`", inline = False)
        show.add_field(name = "Uptime", value = f"`{convert_to_date(uptime)}`")
        show.add_field(name = "Shard(s)", value = "`1`", inline = False)
        show.add_field(name = "Guilds", value = f"`{len(interaction.client.guilds)}`")
        
        await interaction.response.send_message(embed = show)
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AboutBot(bot))    