# Imports
import discord, os
from flask import Flask
from threading import Thread


# Constants
# Note: For your discord bot token, just add an env var named "DISCORD_BOT_TOKEN" with the value.
TODO_CHANNEL_ID = 1544487981031620698
UNLEGIT_USER_ID = 966584910104129556
SUGGESTIONS_CHANNEL_ID = 1544487981031620698

# Flask Setup
app = Flask(__name__)

@app.route('/')
def home() :
    return 'whoopsie! you caught us naughty girls having yuri sex >w< oh nuu~'

def run_flask() :
    app.run(host = '0.0.0.0', port = 10_000)

def keep_alive() :
    server = Thread(target = run_flask, daemon = True)
    server.start()


# Discord Setup
bot = discord.Client(intents = discord.Intents.all())

@bot.event
async def on_ready() :
    print('[LOG] Started having yuri sex~ >w<')
    return

@bot.event
async def on_reaction_add(reaction, user) :
    if reaction.emoji == '❌' and user.id == UNLEGIT_USER_ID and reaction.message.channel.id == SUGGESTIONS_CHANNEL_ID :
        await reaction.message.delete()
    return


# Execution of yuri sex~
if __name__ == '__main__' :
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    keep_alive()
    bot.run(BOT_TOKEN)
