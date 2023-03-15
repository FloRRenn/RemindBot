from discord import ui, TextStyle, Interaction, Embed
from datetime import datetime
from ultils.time_convert import is_valid_with_pattern
from ultils.db_action import Database
from random import randint

def convert_to_timestamp(datetime_string):
    datetime_object = datetime.strptime(datetime_string, '%d/%m/%Y %H:%M')
    timestamp = datetime.timestamp(datetime_object)
    return int(timestamp)

class NewRemind(ui.Modal, title = "Tạo nhắc nhở"):
    title_ = ui.TextInput(label = "Tiêu đề", placeholder = "Nhập tiêu đề", max_length = 100, min_length = 1, style = TextStyle.short, required = True)
    content = ui.TextInput(label = "Nội dung", placeholder = "Nhập nội dung", min_length = 5, style = TextStyle.short, required = False)
    end_date = ui.TextInput(label = "Ngày nhắc nhở", placeholder = f"Nhập ngày nhắc nhở", default = datetime.now().strftime("%d/%m/%Y"), min_length = 8, max_length = 10, style = TextStyle.short, required = True)
    end_time = ui.TextInput(label = "Thời gian nhắc nhở", placeholder = "Nhập thời gian nhắc nhở", default = datetime.now().strftime("%H:%M"), min_length = 3, max_length = 5, style = TextStyle.short, required = True)
    
    def __init__(self, user_mention : int) -> None:
        super().__init__()
        self.mention_id = user_mention
    
    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        
        if not is_valid_with_pattern(self.end_date.value, "date_pattern"):
            return await interaction.followup.send("Ngày không hợp lệ, format phải là d/m/yyyy", ephemeral = True)
        
        end_date_ = datetime.strptime(self.end_date.value, "%d/%m/%Y").date()
        now = datetime.now().date()
        if (now > end_date_):
            return await interaction.followup.send("Ngày không hợp lệ, ngày kết thúc phải lớn hơn ngày bắt đầu", ephemeral = True)
            
        if not is_valid_with_pattern(self.end_time.value, "time_pattern"):
            return await interaction.followup.send("Thời gian không hợp lệ, format phải là hh:mm", ephemeral = True)
        
        remind_id = randint(0, 9999)
        timestmap = convert_to_timestamp(f"{self.end_date.value} {self.end_time.value}")
        mention_ids = [interaction.user.id]
        if self.mention_id is not None:
            mention_ids.append(self.mention_id)
        
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
        
        db = Database("reminder")
        db.insert(data)
        del db
        
        embed = Embed(title = self.title_.value, description = self.content.value, color = 0x00ff00)
        embed.add_field(name = "Ngày nhắc nhở", value = self.end_date.value + " " + self.end_time.value + f"\n<t:{timestmap}:R>")
        embed.set_author(name = f"Remind ID: {remind_id}")
        embed.set_footer(text = f"Người tạo: {interaction.user.name}#{interaction.user.discriminator}")
        
        await interaction.followup.send(f"Tạo nhắc nhở thành công! Bạn có thể chỉnh sửa lại nội dung với `/remind edit_from_id <id>`", embed = embed, ephemeral = True)