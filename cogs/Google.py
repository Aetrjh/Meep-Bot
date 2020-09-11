import discord
from discord.ext import commands


class Google(commands.Cog):

    def __init__(self, client):
        self.client = client


    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Google is online.")

    
    #Commands
    @commands.command()
    async def google(self, ctx):
        await ctx.send("Google!")


def setup(client):
    client.add_cog(Google(client))