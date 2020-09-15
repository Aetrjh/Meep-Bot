import re
from os import path
import itertools
import pytz
from datetime import datetime, timedelta, date

import discord
from discord.ext import commands
import asyncio


class General(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Function for backbround reminders
    async def backgroundReminderChecker(self, userID, reminder, userTimezone, reminderTime, ifPast):

        #Creates timezone variable based on the users entered timezone from timezones.txt to be used for creating a timezone variable.
        timezone = pytz.timezone(userTimezone)

        #Comares the current timezone of the user to the reminderTime based on the timezone of the user.
        while timezone.localize(datetime.now()) < reminderTime:
            await asyncio.sleep(10)

        #If the bot was started and the reminders loaded and did not miss the reminder print the reminder message else print the message saying sorry for the missed reminder in line 71.
        if ifPast == False:
            userToDM = self.client.get_user(int(userID))
            await userToDM.send("Hey, <@{0}>, remember to: {1}".format(userID, reminder))

        #Get the filepath for the reminders.txt file where reminders are stored in case of the bot getting restarted.
        basepath = path.dirname(__file__)
        remindersFilePath = path.abspath(path.join(basepath, "reminders.txt"))

        #Read the lines of reminders.txt file.
        with open(remindersFilePath, "r") as remindersFile:
            reminders = remindersFile.readlines()

        #Rewrite the reminders file for every line excluding the reminder that was just fulfilled.
        with open(remindersFilePath, "w") as remindersFile:
            for reminderLine in reminders:
                reminderArgs = reminderLine.split()
                if reminderLine != "\n":
                    if int(reminderArgs[0]) == userID and reminderArgs[1] == userTimezone and int(reminderArgs[2]) == reminderTime.year and int(reminderArgs[3]) == reminderTime.month and int(reminderArgs[4]) == reminderTime.day and int(reminderArgs[5]) == reminderTime.hour and int(reminderArgs[6]) == reminderTime.minute and reminder == " ".join(reminderArgs[7:]):
                        pass
                    else:
                        remindersFile.write(reminderLine)

    
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("General is online.")
        
        #Set the reminders.txt filepath.
        basepath = path.dirname(__file__)
        remindersFilePath = path.abspath(path.join(basepath, "reminders.txt"))
        
        #Read the reminders.txt file apon starting the bot to load any stored reminders.
        remindersFile = open(remindersFilePath, "r")
        reminders = remindersFile.readlines()
        for reminderLine in reminders:
            if reminderLine != "\n":
                args = reminderLine.split()

                ifPast = False

                #Creates the reminderTime set to the users timezone.
                timezone = pytz.timezone(args[1])
                reminderTime = timezone.localize(datetime(int(args[2]), int(args[3]), int(args[4]), hour = int(args[5]), minute = int(args[6])))

                #Compares the time of the currect user set by the timezone.txt file to the reminderTime and if the time is already past notify the user that we have missed the reminder since restarting.
                if timezone.localize(datetime.now()) > reminderTime:
                    reminder = " ".join(args[7:])

                    userToDM = self.client.get_user(int(args[0]))
                    await userToDM.send(f"Sorry, <@{args[0]}>, we missed your reminder: {reminder}.")

                    #Sets the ifPast variable to True. This is crucial to display only the sorry message above and not the reminder message as well.
                    ifPast = True

                #For each reminder in reminders.txt create a background function for each.
                self.client.loop.create_task(General.backgroundReminderChecker(self, int(args[0]), " ".join(args[7:]), args[1], reminderTime, ifPast))

    
    #Commands
    @commands.command()
    async def general(self, ctx):
        await ctx.send("Genearl!")


    @commands.command()
    async def remind(self, ctx, *args):
        
        #Create a help message to display when the user improperly uses the command.
        helpMessage = "Command args are (day) of the upcomming day or \"Today\" for current day (the name of the current day with give a reminder the next instance of that day), (time) formated hour and minutes including am or pm, and (reminder) the reminder name. Example ({bot_prefix}remind Friday 5:30 pm water plants)".format(bot_prefix = ctx.bot.command_prefix)
        
        #Check to see if the args entered in the reminder command are at least one.
        if len(args) == 0:
            await ctx.send(helpMessage)
            return
        elif args[0] == "help":
            await ctx.send(helpMessage)
            return
        #Test to see if the args are at least four.
        elif len(args) < 4:
            await ctx.send(helpMessage)
            return
        
        #Try to turn the hour and minute into ints and if failed print helpMessage.
        try:
            hour = int(args[1].split(":")[0])
            minute = int(args[1].split(":")[1])
        except ValueError:
            await ctx.send(helpMessage)
            return

        #Sets the accepted characters for the time arg (0-9 and :).
        acceptedCharsForTime = re.compile("[0-9:]")

        #Sets the accepted days of the week for the command.
        days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

        #Test to see if the time entered matches the correct format.
        if not acceptedCharsForTime.match(args[1]) or (args[2].lower() != "am" and args[2].lower() != "pm"):
            await ctx.send(helpMessage)
            return

        #Checks to see if the day entered is in days (a day of the week) or today and that the time entered is formatted to 1 to 12 hours and 0 to 59 minutes.
        elif (args[0].lower() in days or args[0].lower() == "today") and (1 <= hour <= 12) and (0 <= minute <= 59):
            #Adds 12 hours to the hour if pm is used since the datetime object uses a 24 base hour syatem.
            if args[2] == "pm":
                hour += 12
            #Sets hour to 0 if hour equals 12 and am is used since datetime object uses 24 base hour system.
            elif args[2] == "am" and hour == 12:
                hour = 0
            
            #Sets the timezones.txt filepath.
            basepath = path.dirname(__file__)
            timezoneFilePath = path.abspath(path.join(basepath, "timezones.txt"))
            
            #Goes through the timezones.txt file and tries to find the users set timezone set by the timezone command.
            userTimezonesFile = open(timezoneFilePath, "r")
            userTimezones = userTimezonesFile.readlines()
            for userTimezoneLine in userTimezones:
                if int(userTimezoneLine.split()[0]) == ctx.author.id:
                    userTimezone = userTimezoneLine.split()[1]
            
            #Test if the users timzone was not found and if so send an error message.
            try:
                userTimezone
            except NameError:
                await ctx.send(f"You need to set your timezone to properly use this command. A list of timezones can be found at https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568. To set a timezone use {ctx.bot.command_prefix}timezone (timezone). ex ({ctx.bot.command_prefix}timezone America/New_York)")
                return
            
            #Initializes the day counter to 0.
            dayCounter = 0

            #If day entered equals "today" skip over this making daycounter equal to 0.
            if args[0].lower() != "today":
                #Get the current day based on the users timezone
                today = datetime.now(pytz.timezone(userTimezone)).strftime("%A").lower()
                #If the day entered equals the current day make the day counter 7 for the next occurrence of that day.
                if today == args[0].lower():
                    dayCounter = 7
                #Loop trough the days list starting at the index of the current day of the user dased on their timezone and cycle through the days list adding to the day counter until the reminder day is reached to get the offset of days between the reminder day and user current day.
                for day in itertools.chain.from_iterable(itertools.repeat(days[days.index(today):], 1)):
                    if day == args[0].lower():
                        break
                    dayCounter += 1

            #Set the timezone to the users timezone as specified in timezones.txt and create a reminderTime of the date and time to be reminded.
            timezone = pytz.timezone(userTimezone)
            reminderTime = timezone.localize(datetime.now() + timedelta(days = dayCounter))
            reminderTime = reminderTime.replace(hour = hour, minute = minute, second = 0, microsecond = 0)

            #If the reminderTime is already past tell user that time has already past.
            if timezone.localize(datetime.now()) > reminderTime:
                await ctx.channel.send("Looks like that time has already past. You better get to it.")
            else:
                #Create the reminders.txt filepath using basepath from line 141.
                remindersFilePath = path.abspath(path.join(basepath, "reminders.txt"))
                
                #Create the reminder string from the args entered.
                reminder = " ".join(args[3:])
                
                #Open and append reminder data to reminders.txt file.
                remindersFile = open(remindersFilePath, "a")
                remindersFile.write(f"{ctx.author.id} {userTimezone} {reminderTime.year} {reminderTime.month} {reminderTime.day} {hour} {minute} {reminder}\n")
                remindersFile.close()

                #Create a background task for the reminder entered and sends a message notifying the user when the reminder will be.
                self.client.loop.create_task(General.backgroundReminderChecker(self, ctx.author.id, " ".join(args[3:]), userTimezone, reminderTime, False))
                await ctx.send("Okay <@{user_id}>, you will be reminded {reminder} on {day} at {time}".format(user_id = ctx.author.id, reminder = " ".join(args[3:]), day = args[0], time = args[1] + args[2]))
        
        #If all other conditions have failed send helpMessage.
        else:
            await ctx.send(helpMessage)
            return
        
    @commands.command()
    async def timezone(self, ctx, *args):

        #Set the helpMessage.
        helpMessage = f"Please enter {ctx.bot.command_prefix}timezone (timezone). A list of timezones can be found at https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568"
        
        #Check to see if the args entered have a lenght of 1 and the first arg is a valid timezone aka in https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568.
        if len(args) == 1 and args[0] in pytz.all_timezones:

            #Sets the timezones.txt filepath
            basepath = path.dirname(__file__)
            timezoneFilePath = path.abspath(path.join(basepath, "timezones.txt"))

            #Initializes the variable timezonFound to False for later reference.
            timezoneFound = False

            #Reads the text in timezones.txt for later.
            with open(timezoneFilePath, "r") as userTimezonesFile:
                userTimezones = userTimezonesFile.readlines()

            #Replaces the timezone with a new timezone specified in the first arg in the timezone.txt file, all other lines are left as is.
            with open(timezoneFilePath, "w") as userTimezonesFile:
                for userTimezoneLine in userTimezones:
                    if userTimezoneLine != "\n":
                        if int(userTimezoneLine.split()[0]) == ctx.author.id:
                            userTimezonesFile.write(f"{ctx.author.id} {args[0]}\n")
                            #Sets the timezoneFound variable to True to prevent later on the appending of a new timezone.
                            timezoneFound = True
                        else:
                            userTimezonesFile.write(userTimezoneLine)

            #Appends the timezone to the timezones.txt file if prevous data for the timezone was not found for the user.
            if timezoneFound == False:
                with open(timezoneFilePath, "a") as userTimezonesFile:
                    userTimezonesFile.write(f"{ctx.author.id} {args[0]}\n")
                    userTimezonesFile.close()

            #Sends message telling that it has set the timezone
            await ctx.send(f"Timezone set to {args[0]}")

        #If check fails send helpMessage.
        else:
            await ctx.send(helpMessage)



def setup(client):
    client.add_cog(General(client))