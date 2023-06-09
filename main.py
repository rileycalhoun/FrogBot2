### A script that will run a Discord Bot using a token provided by a .env file

# Import the necessary libraries
from discord.ext import commands
from datetime import datetime, time, timedelta
from pytz import timezone
import asyncio, dotenv, logging, os, discord

# Load environment variables from the .env files
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(os.getenv("BOT_NAME"))

# configure the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="fb!", intents=intents)

# configure the time settings
TZ = timezone('Europe/Berlin')
WHEN = time(1, 0, 0) # 1 AM

# get guild and channel ids
guild_id = int(os.getenv('GUILD_ID'))
channel_id = int(os.getenv('CHANNEL_ID'))

### Log the bot in and perform this task:
### Every day at a specific time send a message to a specific channel (which id is provided in the .env file), 
### which contains an image of the day which is taken from the ./images folder by checking what the current date 
### is and then sending the image with the same name as the day of the week.
async def send_frog(channel): # fired once every day
    berlin_time = datetime.now(TZ)
    day_of_week = berlin_time.strftime('%A').lower()
    if day_of_week == "sunday":
        logger.info(f'It is currently {berlin.time()} in Berlin and there is no image for Sunday. FrogBot is taking the day off.')
        return
    image_path = f'./images/{day_of_week}.png'

    with open (image_path, 'rb') as f:
        await channel.send(file=discord.File(f))
        logger.info(f'It is currently {berlin.time()} in Berlin and the image of the day has been sent to channel {channel_id}.')

# frog of the day command
@bot.command()
async def fotd(ctx):
    berlin_time = datetime.now(TZ)
    day_of_week = berlin_time.strftime('%A').lower()
    if day_of_week == "sunday":
        await ctx.channel.send("it's sunday in germany, so i don't have an image to send at the moment <3 check back tomorrow!")
        return

    await send_frog(ctx.channel)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name='the time!', type=discord.ActivityType.watching)) # Change the status
    logger.info("Ready to receive commands and send images!")

async def background_task():
    now = datetime.utcnow().astimezone(TZ)
    if now.time() > WHEN:
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()
        await asyncio.sleep(seconds)

    while(True):
        now = datetime.utcnow()
        target_time = datetime.combine(now.date(), WHEN)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)

        channel = bot.get_guild(guild_id).get_channel(channel_id)
        await send_frog(channel)
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = asyncio.sleep(seconds)

def main():
    bot.run(os.getenv("TOKEN"))
    while(True):
        asyncio.run(background_task())

if __name__ == "__main__":
    main()