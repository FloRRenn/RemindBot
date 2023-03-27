from discord import app_commands, Interaction, Embed
from discord.ext import commands

from ultils.graphQL_query import anime_search, studio_search

class Anime(commands.GroupCog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name = "search_by_name", description = "Tìm kiếm thông tin anime")
    async def _anime(self, interaction : Interaction, anime_name : str):
        await interaction.response.defer(ephemeral = False)
        data = await anime_search(anime_name)
        if not data:
            await interaction.response.send_message("Không tìm thấy anime", ephemeral = True)
            return
        
        embed = Embed(title = f'{data["title"]["romaji"]} ({data["title"]["native"]})', 
                      description = data["description"],
                      color = 0x00ff00)
        embed.set_image(url = data["bannerImage"])
        if data["studios"]["nodes"]:
            embed.set_author(name = "Studio: " + data["studios"]["nodes"][0]["name"], url = data["siteUrl"])
        embed.add_field(name = "Ngày phát hành", value =  f'{data["startDate"]["day"]}/{data["startDate"]["month"]}/{data["startDate"]["year"]}' )
        embed.add_field(name = "Trạng thái", value = data["status"])
        embed.add_field(name = "Nhân vật chính", value = ", ".join([i["name"]["full"] for i in data["characters"]["nodes"]]), inline = False)
        embed.add_field(name = "Số tập", value = data["episodes"])
        embed.add_field(name = "Thời lượng", value = data["duration"])
        if data["nextAiringEpisode"]:
            embed.add_field(name = "Tập tiếp theo", value = data["nextAiringEpisode"]["episode"])
        embed.add_field(name = "Thể loại", value = ", ".join(data["genres"]), inline = False)
        embed.add_field(name = "Độ tuổi", value = "18+" if data["isAdult"] else "13+")
        await interaction.followup.send(embed = embed, ephemeral = False)
        
    @app_commands.command(name = "search_by_studio", description = "Tìm kiếm thông tin studio")
    async def _studio(self, interaction : Interaction, studio : str):
        data = await studio_search(studio)
        if not data:
            return await interaction.response.send_message("Không tìm thấy studio", ephemeral = True)

        animes = ""
        for i in data:
            animes += f'> {i["title"]["romaji"]}\n'
            
        embed = Embed(title = f"Danh sách anime của studio {studio.title()}", 
                      description = animes,
                      color = 0x00ff00)
        await interaction.response.send_message(embed = embed, ephemeral = False)

async def setup(bot : commands.Bot):
    await bot.add_cog(Anime(bot))