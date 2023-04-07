from discord import app_commands, Interaction, TextChannel, Embed, Role
from discord.ext import commands, tasks

from ultils.db_action import Database
from ultils.panels import NewRemind, RemindEditPannel, \
                        is_valid_with_pattern, datetime, convert_to_another_timezone

class Reminder(commands.GroupCog, name = "remind"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.db = Database("reminder")
        self.guild_cache = self.load_default_channels()
        self.remind_checker.start()
    
    def load_default_channels(self):
        res = {}
        data = self.db.get_all({"type" : "default_channel"})
        for guild in data:
            res[guild["guild_id"]] = guild["default_channel"]
        return res
    
    @app_commands.command(name = "set_default_channel", description = "Chọn kênh mặc định để gửi lịch nhắc")
    @commands.has_permissions(administrator = True)
    async def _set_default_channel(self, interaction : Interaction, channel : TextChannel):
        channelID = channel.id
        guildID = interaction.guild.id
        data = {
            "default_channel": channelID,
            "guild_id": guildID,
            "type" : "default_channel"
        }
        self.db.update({"guild_id" : guildID}, {"$set" : data}, upsert = True)
        self.guild_cache[guildID] = channelID
        await interaction.response.send_message(f"Đã thiết lập kênh mặc định là {channel.mention}", ephemeral = True)
        
    @app_commands.command(name = "create", description = "Tạo nhắc nhở mới")
    async def _set_remind(self, interaction : Interaction, mention_role : Role):
        modal = NewRemind(mention_role.id, self.db)
        await interaction.response.send_modal(modal)
        
    @app_commands.command(name = "get", description = "Lấy lịch nhắc từ ID")
    async def _get_remind_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999]):
        remind = self.db.find({"remind_id" : remind_id, "user_id" : interaction.user.id})
        if remind:
            embed = Embed(title = remind["title"], description = remind["content"], color = 0x00ff00)
            embed.add_field(name = "Ngày nhắc nhở", value = remind["end_date"] + " " + remind["end_time"] + f"\n<t:{remind['timestamp']}:R>")
            embed.set_author(name = f"Remind ID: {remind['remind_id']}")
            
            user = ""
            for user_id in remind["mention_id"]:
                user += f"<@{user_id}> "
            embed.add_field(name = "Người được nhắc", value = user)
            
            await interaction.response.send_message(embed = embed, ephemeral = True)
        
        else:
            await interaction.response.send_message(f"Không tìm thấy lịch nhắc có ID {remind_id}", ephemeral = True)
        
    @app_commands.command(name = "list_remind", description = "Xem danh sách lịch nhắc của bạn")
    async def _list_remind(self, interaction : Interaction):
        query = { "user_id" : interaction.user.id}
        list_reminds = self.db.get_all(query)
        
        remind_to_text = ""
        for remind in list_reminds:
            remind_to_text += f"**➡️ ID: {remind['remind_id']} - {remind['title']} - Ngày nhắc: {remind['end_date']} {remind['end_time']}** (<t:{remind['timestamp']}:R>)\n"
        
        if remind_to_text != "":   
            embed = Embed(title = "Danh sách lịch nhắc bạn", description = remind_to_text, colour = 0x00ff00)
            return await interaction.response.send_message(embed = embed, ephemeral = True)
        
        await interaction.response.send_message("**Bạn không có lịch nhắc nào**", ephemeral = True)
        
    @app_commands.command(name = "delete", description = "Xóa lịch nhắc của bạn")
    async def _delete_from_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999]):
        query = { "user_id" : interaction.user.id, "remind_id" : remind_id}
        result = self.db.remove(query)
        
        if result.deleted_count != 0:
            await interaction.response.send_message("**Đã xóa thành công**", ephemeral = True)
        else:
            await interaction.response.send_message("**Không tìm thấy lịch nhắc**", ephemeral = True)
            
    @app_commands.command(name = "edit", description = "Sửa lịch nhắc của bạn")
    async def _edit_from_id(self, interaction : Interaction, remind_id : app_commands.Range[int, 0, 9999]):
        data = {"remind_id" : remind_id, "user_id" : interaction.user.id}
        remind_data = self.db.find(data)
        if not remind_data:
            return await interaction.response.send_message(f"**Không tìm thấy lịch nhắc có id {remind_id}**", ephemeral = True)
        
        channel = self.db.find({"type" : "default_channel", "guild_id" : interaction.guild.id})
        pannelEdit = RemindEditPannel(self.db, remind_data, channel["default_channel"], title = f"Edit remind ID {remind_id}")
        await interaction.response.send_modal(pannelEdit)

    async def _send_embed(self, remind, content, is_update = False, color = 0x00ff00):
        channel = self.bot.get_channel(self.guild_cache[remind["guild_id"]])
        message = await channel.fetch_message(remind['message_id'])
        await message.delete()
        
        embed = message.embeds[0]
        user = f"<@&{remind['mention_id']}> - {content}"
        
        embed = Embed(title = remind["title"], description = remind["content"], color = color)
        embed.set_footer(text = f"Remind ID: {remind['remind_id']}")
        if not is_update:
            embed.set_thumbnail(url = "https://cdn-icons-png.flaticon.com/512/6459/6459980.png")
        
        message = await channel.send(user, embed = embed)
        if is_update:
            self.db.update({"remind_id" : remind["remind_id"], "user_id" : remind["user_id"]}, {"$set" : {"message_id" : message.id}})
    
    @tasks.loop(minutes = 2)
    async def remind_checker(self):
        query = {"type" : "reminder"}
        reminds_list = self.db.get_all(query)
        documents_count = self.db.count(query)
        
        if documents_count != 0:
            alignment = 120 // documents_count
            timestmap = datetime.now().timestamp()
            
            _24h = 24 * 60 * 60 + timestmap
            _6h = 6 * 60 * 60 + timestmap
            
            for remind in reminds_list:
                if timestmap >= remind["timestamp"]:
                    self.db.remove({"remind_id" : remind["remind_id"], "user_id" : remind["user_id"]})
                    await self._send_embed(remind, "**Đã dến thời gian**")
                    
                elif _6h - 150 <= remind["timestamp"] <= _6h:
                    await self._send_embed(remind, "**6h nữa là dead rồi, lẹ đi.**", True, 0xF99B00)
                    
                elif _24h - 150 <= remind["timestamp"] <= _24h:
                    await self._send_embed(remind, "**Còn khoảng 24h nữa là đến deadline rồi mấy cậu. Tốc độ lên :v**", True, 0xF9DE00)
                    
                timestmap += alignment
                
    @remind_checker.before_loop
    async def before_remind_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot : commands.Bot):
    await bot.add_cog(Reminder(bot))