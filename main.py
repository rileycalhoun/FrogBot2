### A script that will run a Discord Bot using a token provided by a .env file

# Import the necessary libraries
import discord, dotenv, os, pytz, logging
from discord.ext import commands

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load environment variables from the .env files
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

bot_name = os.getenv('BOT_NAME')
logger = logging.getLogger(bot_name)

### Log the bot in and perform this task:
### Every day at a specific time send a message to a specific channel (which id is provided in the .env file), 
### which contains an image of the day which is taken from the ./images folder by checking what the current date 
### is and then sending the image with the same name as the day of the week.
async def send_image_of_the_day(channel):

    berlin = datetime.now(pytz.timezone('Europe/Berlin'))
    # Get the current day of the week
    day_of_week = berlin.strftime('%A').lower()

    # Get the channel ID from the environment variables
    channel_id = int(os.getenv('CHANNEL_ID'))

    # Get the path to the image file
    image_path = f'./images/{day_of_week}.png'

    # Send the image to the channel
    with open(image_path, 'rb') as f:
        await channel.send(file=discord.File(f))
    logger.info(f'It is currently {berlin.time()} in Berlin and the image of the day has been sent to channel {channel_id}.')

intents = discord.Intents.default()
intents.message_content = True

# Create an instance of the client
client = commands.Bot(command_prefix='!', intents=intents)

# Define and add !fotd command
@client.command()
async def fotd(ctx):
    await send_image_of_the_day(ctx.channel)

# Create an instance of the scheduler
scheduler = AsyncIOScheduler()

# Schedule the send_image_of_the_day function to run every day at a specific time
scheduler.add_job(send_image_of_the_day(client.get_channel(os.getenv("CHANNEL_ID"))), 'cron', hour=13, minute=0, args=[client])

# Start the scheduler
scheduler.start()

@client.event
async def on_ready():
    logger.info("Ready to receive commands and send images!")

# Log in with the token
client.run(os.getenv('DISCORD_TOKEN')) # Token goes here