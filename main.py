import os
import discord
from discord.ext import tasks
import asyncio
import datetime as dt
import pytz  # Import pytz for timezone handling
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_TIME = (10, 0)  # Replace with your desired time (Hour, Minute) in 24-hour format

# Define intents for the bot
intents = discord.Intents.default()
intents.messages = True

# Create a Discord client instance with the defined intents
client = discord.Client(intents=intents)

# Define an event for when the bot is ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Start the daily_message and print_remaining_time tasks when the bot is ready
    daily_message.start()
    print_remaining_time.start()

# Create a loop that runs every minute to check if it's time to send the daily message
@tasks.loop(minutes=1)
async def daily_message():
    now_utc = dt.datetime.now(pytz.utc)
    now_cest = now_utc.astimezone(pytz.timezone('CET'))
    target_time = dt.time(*MESSAGE_TIME)

    if now_cest.time() >= target_time and (now_cest - daily_message.last_sent).seconds >= 60:
        channel = client.get_channel(CHANNEL_ID)

        if channel:
            day_of_week = now_cest.strftime('%A').lower()
            image_file = f"images/{day_of_week}.jpg"

            if os.path.exists(image_file):
                with open(image_file, 'rb') as img:
                    await channel.send(file=discord.File(img))
            else:
                await channel.send(f"Image for {day_of_week.capitalize()} not found.")

            daily_message.last_sent = now_cest.astimezone(pytz.timezone('CET'))
        else:
            logging.warning(f'Channel with ID {CHANNEL_ID} not found.')

# Create a loop that runs every 10 minutes to print the remaining time
@tasks.loop(minutes=10)
async def print_remaining_time():
    now_utc = dt.datetime.now(pytz.utc)
    now_cest = now_utc.astimezone(pytz.timezone('CET'))
    target_time = dt.time(*MESSAGE_TIME)
    future_target = dt.datetime.combine(now_cest.date(), target_time)

    if now_cest.time() >= target_time:
        future_target += dt.timedelta(days=1)

    future_target_utc = future_target.astimezone(pytz.utc)
    time_until_target = (future_target_utc - now_utc).seconds

    logging.info(f"Time until sending message: {time_until_target // 3600} hours, {(time_until_target // 60) % 60} minutes, {time_until_target % 60} seconds")

# Define a function to run before the daily_message task starts
@daily_message.before_loop
async def before_daily_message():
    now_utc = dt.datetime.now(pytz.utc)
    now_cest = now_utc.astimezone(pytz.timezone('CET'))
    target_time = dt.time(*MESSAGE_TIME)
    future_target = dt.datetime.combine(now_cest.date(), target_time)

    if now_cest.time() >= target_time:
        future_target += dt.timedelta(days=1)

    future_target_utc = future_target.astimezone(pytz.utc)
    time_until_target = (future_target_utc - now_utc).seconds
    await asyncio.sleep(time_until_target)

    # Set the last_sent time to the current CEST time
    daily_message.last_sent = now_cest.astimezone(pytz.timezone('CET'))

# Define a function to run before the print_remaining_time task starts
@print_remaining_time.before_loop
async def before_print_remaining_time():
    # Sleep until the first 10-minute mark
    now_utc = dt.datetime.now(pytz.utc)
    time_until_next_ten = 600 - (now_utc.minute % 10) * 60 - now_utc.second
    await asyncio.sleep(time_until_next_ten)

# Run the bot using the provided token
client.run(TOKEN)
