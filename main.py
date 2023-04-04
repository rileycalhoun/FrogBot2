import os
import discord
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Set up intents
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Set up scheduler
scheduler = AsyncIOScheduler()
scheduler.configure(timezone='Europe/Berlin')

# Function to send image to channel
async def send_image():
    # Get current day of the week
    day_of_week = datetime.now().strftime('%A').lower()
    # Set image path based on day of week
    image_path = f'images/{day_of_week}.png'
    # Get channel
    channel = client.get_channel(CHANNEL_ID)
    # Send image to channel
    await channel.send(file=discord.File(image_path))

# Schedule send_image function to run at 10AM every day
scheduler.add_job(send_image, 'cron', hour=10)
scheduler.start()

# Function to log time remaining until next message
async def log_time_remaining():
    next_run_time = scheduler.get_job('send_image').next_run_time
    time_remaining = next_run_time - datetime.now()
    logging.info(f'Time remaining until next message: {time_remaining}')

# Schedule log_time_remaining function to run every 10 minutes
scheduler.add_job(log_time_remaining, 'interval', minutes=10)

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    await send_image()

client.run(TOKEN)