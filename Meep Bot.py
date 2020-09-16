#This imports the API key secrets from a hidden seperate file.
import config

import discord
import os
from discord.ext import commands

#Sets the bot prefix.
client = commands.Bot(command_prefix = "~")

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    
#Loads each cog/extension.
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

#Runs the bot with the hidden API key. You must set your own API key here for the bot to run.
client.run(config.discordAPIKey)