import discord
from discord.ext import commands

from dotenv import load_dotenv
from os import getenv

import logging
import logging.handlers

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = "$$", intents = discord.Intents.all())
        
    async def setup_hook(self):
        cogs = ["bot.about", "bot.cmd",
                "server.channel", "server.delete"]
                #"errors"]
        for cog in cogs:
            await self.load_extension(f"cogs.{cog}")
        
        await self.tree.sync() 
        
    async def on_ready(self):
        print(f'{self.user} is online') 
        
def setup_log():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(
        filename = 'discord.log',
        encoding = 'utf-8',
        maxBytes = 8 * 1024 * 1024,
        backupCount = 2
    )
    dt_fmt = '%d/%m/%Y %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

if __name__ == "__main__":
    setup_log()
    load_dotenv()
    
    TOKEN = getenv("TOKEN")
    bot = Bot()   
    bot.run(TOKEN)