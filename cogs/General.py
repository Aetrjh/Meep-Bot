import datetime

import discord
from discord.ext import commands, timers
import asyncio


class General(commands.Cog):

    def __init__(self, client):
        self.client = client


    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("General is online.")

    
    #Commands
    @commands.command()
    async def general(self, ctx):
        await ctx.send("Genearl!")

    async def backgroundReminderChecker(self, timer, ctx):
        while timer > 0:
            timer -= 10
            await asyncio.sleep(10)
        await ctx.send("Hey, <@{0}>, remember to: {1}".format(userID, "reminder"))

    @commands.command()
    async def remind(self, ctx):
        timer = 30
        self.client.loop.create_task(General.backgroundReminderChecker(self, timer, ctx))


def setup(client):
    client.add_cog(General(client))
