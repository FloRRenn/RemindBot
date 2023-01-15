from dotenv import load_dotenv
from os import getenv

def is_botOnwer(interaction):
    load_dotenv()
    
    onwerID = int(getenv("ONWERID"))
    userID = interaction.user.id
    if onwerID == userID:
        return True
    return False