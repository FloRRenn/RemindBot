from discord import app_commands, Interaction, Member, NotFound, Forbidden, HTTPException 
from discord.ext import commands
from typing import Optional
from ultils.time_convert import timedelta_format

class Moderator(commands.GroupCog, name = "mod"):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name = "ban", description = "Ban user")
    @commands.has_permissions(moderate_members = True)
    async def _ban(self, interaction : Interaction, user : Member, reason : Optional[str] = ""):
        if interaction.user.id == user.id:
            return interaction.response.send_message("Bạn không thể tự ban chính bản thân.", ephemeral = True)
        
        username = user.display_name + "#" + user.discriminator
        try:
            await user.ban(reason = reason)
            await interaction.response.send_message(f"user **{username}** đã bị ban khỏi server với lý do: **{reason}**")
        except Forbidden:
            await interaction.response.send_message("Bạn không được quyền sử dụng lệnh này.", ephemeral = True)
        except HTTPException:
            await interaction.response.send_message(f"Bạn không thể ban {user.mention}", ephemeral = True)
        
    @app_commands.command(name = "unban", description = "Unban user")
    @commands.has_permissions(moderate_members = True)
    async def _unban(self, interaction : Interaction, user : Member, reason : Optional[str] = ""):
        if interaction.user.id == user.id:
            return interaction.response.send_message("Bruh, tự unban bản thân.", ephemeral = True)
        
        try:
            await interaction.guild.unban(user = user, reason = reason)
            await interaction.response.send_message(f"Đã unban user {user.mention}")
        except NotFound:
            await interaction.response.send_message("Không tìm thấy user trong danh sách Ban", ephemeral = True)
        except Forbidden:
            await interaction.response.send_message("Bạn không được quyền sử dụng lệnh này.", ephemeral = True)
            
    @app_commands.command(name = "kick", description = " kick a user")
    @commands.has_permissions(moderate_members = True)
    async def _kick(self, interaction : Interaction, user : Member, reason : Optional[str] = ""):
        if interaction.user.id == user.id:
            return interaction.response.send_message("Bruh, tự kick bản thân.", ephemeral = True)
        
        username = user.display_name + "#" + user.discriminator
        try:
            await user.kick(reason = reason)
            await interaction.response.send_message(f"Đã kick user **{username}** ra khỏi server")
        except Forbidden:
            await interaction.response.send_message("Bạn không được quyền sử dụng lệnh này.", ephemeral = True)
        except HTTPException:
            await interaction.response.send_message(f"Bạn không thể kick {user.mention}", ephemeral = True)
            
    @app_commands.command(name = "mute_user", description = "Mute user")
    @commands.has_permissions(moderate_members = True)
    async def _timeout(self, interaction : Interaction, user: Member, reason: Optional[str], 
                       days: app_commands.Range[int, 0, 30] = 0, hours: app_commands.Range[int, 0, 24] = 1, 
                       minutes: app_commands.Range[int, 0, 60] = 0, seconds: app_commands.Range[int, 0, 60] = 0):
        if interaction.user.id == user.id:
            return interaction.response.send_message("Bruh, tự timeout bản thân.", ephemeral = True)
        
        timestamp = timedelta_format(days, hours, minutes, seconds)
        await user.timeout(until = timestamp, reason = reason)
        await interaction.response.send_message(f"Đã timeout user {user.mention} trong {hours}:{minutes}:{seconds}", ephemeral = False)

async def setup(bot : commands.Bot):
    await bot.add_cog(Moderator(bot))