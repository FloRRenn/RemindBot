from discord import app_commands, Interaction, Embed, Member, PermissionOverwrite, Role
from discord.ext import commands

from typing import Optional
import time

from ultils import covert_str_to_seconds, convert_to_date
from ultils import Database

class ManageChannel(commands.GroupCog, name = "channel"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("rooms")
        
    async def addChannel(self, onwerID, channelID, guildID, time_remain):
        data = {
            "onwerID": onwerID,
            "channelID": channelID,
            "guildID": guildID,
            "timeToFinish": time_remain + time.time()
        }
        self.db.insert(data)
        
    async def check_user(self, memberID, channelID, name):
        find = self.db.find({"onwerID" : memberID, name : channelID})
        if find:
            return True
        return False
        
    async def modifyChannel(self, interaction : Interaction, type : bool, user, role):
        member = interaction.user
        channel = interaction.channel
        
        check = await self.check_user(member.id, channel.id, "channelID")
        if not check:
            return await interaction.response.send_message(f"Bạn không phải chủ phòng này")
        
        if user:
            await channel.set_permissions(user, read_messages = type, send_messages = type, view_channel = type)
            
        if role:
           await channel.set_permissions(role, read_messages = type, send_messages = type, view_channel = type) 
           
        await interaction.response.send_message("Đã thay đổi thành công", ephemeral = True)
        
    @app_commands.command(name = "create", description = "Tạo kênh")
    async def _create(self, interaction : Interaction, channel_name : Optional[str], time : Optional[str] = "1h"):
        await interaction.response.defer()
        
        float_seconds = covert_str_to_seconds(time)
        if float_seconds is None:
            return await interaction.followup.send("Định dạng time bị sai, chỉ sử dụng `s, m, h, d` tương ứng với **giây, phút, giờ, ngày**\nVí dụ: 30s, 10m, 1.5h, 3d...")
        
        if float_seconds > 7 * 24 * 60 * 60: # 7 days
            return await interaction.followup.send("Thời gian tối đa là 1 tuần.")
        
        if channel_name is None:
            channel_name = interaction.user.display_name + "-private"
            
        member = interaction.user
        guild = interaction.guild
        
        find = await self.check_user(member.id, guild.id, "guildID")
        if find:
            return await interaction.followup.send(f"Phòng vẫn còn được sử dụng nên không thể tạo phòng khác", ephemeral = True)
        
        overwrites = {
                guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
                guild.me: PermissionOverwrite(read_messages=True, send_messages=True),
                member: PermissionOverwrite(read_messages=True, send_messages=True)
            }
        
        channel = await guild.create_text_channel(channel_name, overwrites = overwrites)
        await self.addChannel(member.id, channel.id, guild.id, float_seconds)
        
        await interaction.followup.send(f"Kênh {channel.mention} đã được tạo!", ephemeral = True)
        
        show = Embed(title = "Private room", colour = 0x0FDDDA)
        show.add_field(name = "Chủ Phòng", value = f"{member.display_name}#{member.discriminator}")
        show.add_field(name = "Thời gian sử dụng", value = f"`{convert_to_date(float_seconds)}`")
        show.add_field(name = "Hướng dẫn sử dụng (Chỉ có chủ phòng mới được sử dụng)", value = f"`/channel add_user` : Thêm member vào phòng \n `/channel kick_user` : Kick user ra khỏi phòng \n`/channel delete`: Xóa phòng \n`/channel save` : Lưu toàn chat trong phòng thành file", inline = False)
        await channel.send(embed = show)
        
    @app_commands.command(name = "delete", description = "Xóa phòng của bạn")
    async def _delete(self, interaction : Interaction):
        channel = interaction.channel
        member = interaction.user
        
        check = await self.check_user(member.id, channel.id, "channelID")
        if not check:
            return await interaction.response.send_message(f"Bạn không phải chủ phòng này")
        
        data = {
            "onwerID": member.id,
            "channelID": channel.id,
        }
        self.db.remove(data)
        try:
            await channel.delete()
        except:
            await interaction.response.send_message("Xảy ra lỗi khi xóa phòng. Dường như phòng đã bị xóa từ trước đó.", ephemeral = True)
        
    @app_commands.command(name = "add_user", description = "Thêm user/role vào phòng của bạn")
    async def _add_user(self, interaction : Interaction, user : Optional[Member], role : Optional[Role]):
        await self.modifyChannel(interaction, True, user, role)
        
    @app_commands.command(name = "kick_user", description = "Kick user/role ra khỏi phòng của bạn")
    async def _kick_user(self, interaction : Interaction, user : Optional[Member], role : Optional[Role]):
        await self.modifyChannel(interaction, False, user, role)
        
    # @app_commands.command(name = "test")
    # async def _test(self, interaction : Interaction):
    #     await interaction.response.send_message("Sent key")
    #     db = await getDB("rooms")
    #     test_key = {
    #         "aa" : 1212342
    #     }
    #     await db.insert(test_key)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(ManageChannel(bot))
    