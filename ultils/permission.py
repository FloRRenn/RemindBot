from dotenv import load_dotenv
from os import getenv
from discord import app_commands, Interaction

def is_botOnwer():
    def checkUser(interaction : Interaction):
        load_dotenv()

        onwerID = int(getenv("ONWERID"))
        userID = interaction.user.id
        if onwerID == userID:
            return True
        return False
    
    return app_commands.check(checkUser)