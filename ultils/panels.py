from discord import ui, TextStyle, Interaction, Embed, TextChannel
from datetime import datetime
from ultils.time_convert import is_valid_with_pattern
from random import randint

def convert_to_timestamp(datetime_string):
    datetime_object = datetime.strptime(datetime_string, '%d/%m/%Y %H:%M')
    timestamp = datetime.timestamp(datetime_object)
    return int(timestamp)

class NewRemind(ui.Modal, title = "Tạo nhắc nhở"):
    title_ = ui.TextInput(label = "Tiêu đề", placeholder = "Nhập tiêu đề", min_length = 5, max_length = 100, style = TextStyle.short, required = True)
    content = ui.TextInput(label = "Nội dung", placeholder = "Nhập nội dung", min_length = 5, style = TextStyle.paragraph, required = False)
    end_date = ui.TextInput(label = "Ngày nhắc nhở (dd/mm/yyyy)", placeholder = f"Nhập ngày nhắc nhở", default = datetime.now().strftime("%d/%m/%Y"), min_length = 8, max_length = 10, style = TextStyle.short, required = True)
    end_time = ui.TextInput(label = "Thời gian nhắc nhở (hh:mm)", placeholder = "Nhập thời gian nhắc nhở", default = datetime.now().strftime("%H:%M"), min_length = 3, max_length = 5, style = TextStyle.short, required = True)
    
    def __init__(self, user_mention : int, db) -> None:
        super().__init__()
        self.mention_id = user_mention
        self.db = db
    
    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        
        if not is_valid_with_pattern(self.end_date.value, "date_pattern"):
            return await interaction.followup.send("Ngày không hợp lệ, format phải là d/m/yyyy", ephemeral = True)
            
        if not is_valid_with_pattern(self.end_time.value, "time_pattern"):
            return await interaction.followup.send("Thời gian không hợp lệ, format phải là hh:mm", ephemeral = True)
        
        timestmap = convert_to_timestamp(f"{self.end_date.value} {self.end_time.value}")
        timestmap_now = int(datetime.timestamp(datetime.now())) + 30*60
        if timestmap < timestmap_now:
            return await interaction.followup.send("Thời gian nhắc nhở phải sau 30 phút kể từ thời điểm hiện tại.", ephemeral = True)
        
        mention_ids = [interaction.user.id]
        if self.mention_id is not None:
            mention_ids.append(self.mention_id)
        
        remind_id = randint(0, 9999)
        data = {
            "type" : "reminder",
            "remind_id" : remind_id,
            "user_id" : interaction.user.id,
            "guild_id" : interaction.guild.id,
            "mention_id" : mention_ids,
            "title" : self.title_.value,
            "content" : self.content.value,
            "end_date" : self.end_date.value,
            "end_time" : self.end_time.value,
            "timestamp" : timestmap,
        }
        self.db.insert(data)
        
        embed = Embed(title = self.title_.value, description = self.content.value, color = 0x00ff00)
        embed.add_field(name = "Ngày nhắc nhở", value = self.end_date.value + " " + self.end_time.value + f"\n<t:{timestmap}:R>")
        embed.set_author(name = f"Remind ID: {remind_id}")
        embed.set_footer(text = f"Người tạo: {interaction.user.name}#{interaction.user.discriminator}")
        
        await interaction.followup.send(f"Tạo nhắc nhở thành công! Bạn có thể chỉnh sửa lại nội dung với `/remind edit_from_id <id>`", embed = embed, ephemeral = True)
        
class VotePanel(ui.Modal):    
    # title_ = ui.TextInput(label = "Tiêu đề", placeholder = "Nhập tiêu đề", min_length = 5, max_length = 100, style = TextStyle.short, required = True)
    
    def __init__(self, id_ : int, num_of_vote : int, description : str, textchannel : TextChannel, thumbnail, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.id_ = id_
        self.description = description
        self.num_of_vote = num_of_vote
        self.textchannel = textchannel
        self.thumbnail = thumbnail
        self.db = db
        
        for i in range(num_of_vote):
            self.add_item(ui.TextInput(label = f"Vote {i+1}", placeholder = f"Nhập nội dung vote {i+1}", min_length = 5, max_length = 100, style = TextStyle.short, required = True))
    
    async def on_submit(self, interaction: Interaction) -> None:
        embed = Embed(title = f"{self.title}", description = self.description, color = 0x00ff00)
        embed.set_author(name = f"Vote ID: {self.id_}")
        for i in range(self.num_of_vote):
            embed.add_field(name = f"👉 Vote {i+1}", value = self.children[i].value, inline = False)
        embed.set_footer(text = f"Người tạo: {interaction.user.name}#{interaction.user.discriminator}")
        if self.thumbnail:
            embed.set_thumbnail(url = self.thumbnail)
        
        message = await self.textchannel.send("Chọn một trong các emoji ở bên dưới để vote", embed = embed)
        if self.num_of_vote == 1:
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            
        else:
            emojes = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for i in range(self.num_of_vote):
                await message.add_reaction(emojes[i])
        
        await interaction.response.send_message(f"Đã gửi vote đến kênh {self.textchannel.mention}", ephemeral = True)

        data = {
            "vote_id" : self.id_,
            "guild_id" : interaction.guild.id,
            "message_id" : message.id,
            "channel_id" : self.textchannel.id,
            "user_id" : interaction.user.id,
            "num_of_vote" : self.num_of_vote,
            "title" : self.title,
            "description" : self.description,
            "votes" : [i.value for i in self.children]
        }
        self.db.insert(data)
        
class VoteEditPanel(ui.Modal):
    def __init__(self, vote_id, num_of_vote, 
                 description, thumbnail,
                 vote_contents,
                 channel_id, message_id, db, 
                 *args, **kwags) -> None:
        super().__init__(*args, **kwags)
        
        self.db = db
        self.channel_id = channel_id
        self.message_id = message_id
        self.vote_id = vote_id
        
        self.description = description
        self.thumbnail = thumbnail
        
        for i in range(num_of_vote):
            self.add_item(ui.TextInput(label = f"Vote {i+1}", placeholder = f"Nhập nội dung vote {i+1}", default = vote_contents[i], min_length = 5, max_length = 100, style = TextStyle.short, required = True))
            
    async def on_submit(self, interaction: Interaction) -> None:    
        user_id = interaction.user.id
        data = {
            "user_id" : user_id,
            "vote_id" : self.vote_id,
            "votes" : [i.value for i in self.children]
        }
        
        channel = interaction.client.get_channel(self.channel_id)
        message = await channel.fetch_message(self.message_id)
        
        embed = message.embeds[0]
        for i in range(len(self.children)):
            embed.set_field_at(i, name = f"👉 Vote {i+1}", value = self.children[i].value)
            
        if self.thumbnail:
            embed.set_thumbnail(url = self.thumbnail)
            data["thumbnail"] = self.thumbnail
            
        if self.description:
            embed.description = self.description
            data["decsription"] = self.description
        
        self.db.update({"user_id" : user_id},{"$set" : data}) 
        await message.edit(embed = embed)
        await interaction.response.send_message("Đã chỉnh sửa vote thành công!", ephemeral = True)
        
    async def on_error(self, interaction: Interaction, error) -> None:
        await interaction.response.send_message("Đã có lỗi xảy ra, xem lại thông tin!", ephemeral = True)
    
    