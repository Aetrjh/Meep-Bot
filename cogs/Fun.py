import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client


    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun is online.")

    
    #Commands
    @commands.command()
    async def fun(self, ctx):
        await ctx.send("Fun!")


def setup(client):
    client.add_cog(Fun(client))