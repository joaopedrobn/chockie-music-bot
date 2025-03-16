import discord
from discord.ext import commands
import logging
from music import Music
import os
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='ck!', intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(Music(bot))
    logger.info(f'Bot conectado como {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado.")
    else:
        raise error
    
import os
os.system("ffmpeg -version")


load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise ValueError("ERRO: O DISCORD_TOKEN não foi encontrado!")

bot.run(DISCORD_TOKEN)