from discord import app_commands, Interaction, Member, TextChannel, Attachment, PartialMessageable
from discord.ext import commands
from typing import Optional

class TestCMD(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.list_anoynimous = {}
        
    @app_commands.command(name = "anoynimous_edit", description = "Chỉnh sửa channel gửi tin nhắn nặc danh")
    async def edit_id(self, interaction : Interaction, channel_id : str):
        try:
            channel = await self.bot.fetch_channel(int(channel_id))
            self.list_anoynimous[interaction.user.id] = channel.id
            await interaction.response.send_message(f"Tin nhắn sẽ được gửi đến {channel.mention}", ephemeral = True)
            
        except:
            await interaction.response.send_message(f"Không tìm thấy kênh có ID `{channel_id}`", ephemeral = True)
        
    @app_commands.command(name = "anoynimous", description = "Dùng bot để chửi thằng khác")
    async def send_anoynimous_msg(self, interaction : Interaction, message : str, 
                                  file : Optional[Attachment],
                                  send_to : Optional[TextChannel]):
        await interaction.response.defer(ephemeral = True)
        
        if len(message) >= 2000:
            return await interaction.followup.send("Tin nhắn quá dài", ephemeral = False)    
        
        if isinstance(interaction.channel, PartialMessageable):
            def check(message):
                return message.author.id == interaction.user.id
            
            userID = interaction.user.id
            if userID not in self.list_anoynimous:
                await interaction.followup.send("Hãy nhập ID kênh sẽ gửi tin nhắn đến", ephemeral = True)  
                isOke = False
                try:
                    for i in range(3):
                        msg = await interaction.client.wait_for('message', check = check, timeout = 60)
                        
                        try:
                            channelID = int(msg.content)
                            send_to = await self.bot.fetch_channel(channelID)
                            
                            self.list_anoynimous[userID] = channelID
                            isOke = True
                            break
                        except:
                            await interaction.followup.send("Đm ID của kênh loz nào vậy? Kiếm không thấy, nhập lại cái ID đi (Cho mày 60 giây để làm)") 
                except:
                    return await interaction.followup.send("Hết 60 giây và m vẫn không đưa t cái ID nào :v")
                if not isOke:
                    return await interaction.followup.send("Đéo đưa ID kênh, vậy t gửi đi đâu? Nghỉ, đéo làm nữa.")
                
            else:
                send_to = await self.bot.fetch_channel(self.list_anoynimous[userID])
                
        else:
            if send_to is None:
                send_to = interaction.channel
            
        list_webhooks = await send_to.webhooks()
        if len(list_webhooks) == 0:
            webhook = await send_to.create_webhook(name = "Anoynimous")
        else:
            webhook = list_webhooks[0]
            
        if file:
            await webhook.send(content = message, file = await file.to_file())
        else:
            await webhook.send(content = message)
            
        await interaction.followup.send("Đã gửi đến kênh " + send_to.mention, ephemeral = False)
        
        
async def setup(bot : commands.Bot):
    await bot.add_cog(TestCMD(bot))
