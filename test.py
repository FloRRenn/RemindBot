import json
from mdutils.mdutils import MdUtils
from mdutils import Html
from datetime import datetime

def write_md_file(filename, data, username):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    with open(filename, "w+", encoding = "utf-8") as f:
        f.write(f"Cuộc trò chuyện với {username} (Tạo ngày {now}):\n")
        f.write("========================================\n\n")
        
        for conver in data:
            if conver["role"] == "system" or conver["role"] == "assistant":
                who = "## Bot:\n"
            else:
                who = f"## {username}:\n"
            
            f.write(who)
            f.write(f"{conver['content']}\n<br/><br/> \n\n")

data = json.load(open("test.json", "r", encoding = "utf-8"))
username = "test"
filename = "test.md"
write_md_file(filename, data["default"], username)
                
            
        