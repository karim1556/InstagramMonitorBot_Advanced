import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
from monitor import is_account_banned
from database import add_user, get_all_targets, load_users, save_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# Load configuration
with open("config.json") as f:
    config = json.load(f)

DISCORD_TOKEN = config["discord_token"]  # You'll need to add this to your config.json
check_interval = config["check_interval"]
status_cache = {}

# Set up Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()
    check_accounts.start()

@bot.tree.command(name="start", description="Start the Instagram Monitor Bot")
async def start(interaction: discord.Interaction):
    welcome_message = (
        "👋 Welcome to Instagram Monitor Bot!\n"
        "\n"
        "Commands:\n"
        "`/add <username>` – Add a username to monitor\n"
        "`/list` – View your tracked usernames\n"
        "`/remove <username>` – Remove a tracked username\n"
        "`/status <username>` – Check current status of a username"
    )
    await interaction.response.send_message(welcome_message)

@bot.tree.command(name="add", description="Add an Instagram username to monitor")
async def add(interaction: discord.Interaction, username: str):
    username = username.strip("@").lower()
    add_user(str(interaction.user.id), username)
    await interaction.response.send_message(f"✅ Now monitoring @{username}")

@bot.tree.command(name="list", description="List all tracked usernames")
async def list_usernames(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_users()
    if user_id not in data or not data[user_id]["targets"]:
        await interaction.response.send_message("❌ You aren't tracking any usernames.")
        return
    
    targets = data[user_id]["targets"]
    msg = "📋 You are monitoring:\n" + "\n".join([f"• @{username}" for username in targets])
    await interaction.response.send_message(msg)

@bot.tree.command(name="remove", description="Remove a username from monitoring")
async def remove(interaction: discord.Interaction, username: str):
    username = username.strip("@").lower()
    user_id = str(interaction.user.id)
    data = load_users()
    
    if user_id in data and username in data[user_id]["targets"]:
        data[user_id]["targets"].remove(username)
        save_users(data)
        await interaction.response.send_message(f"❌ Stopped monitoring @{username}")
    else:
        await interaction.response.send_message(f"@{username} was not being tracked.")

@bot.tree.command(name="status", description="Check status of a username")
async def status(interaction: discord.Interaction, username: str):
    username = username.strip("@").lower()
    try:
        result = is_account_banned(username)
        if result is None:
            await interaction.response.send_message("⚠️ Couldn't check status. Instagram might be blocking requests.")
        else:
            await interaction.response.send_message(f"@{username} is currently {'❌ BANNED' if result else '✅ ACTIVE'}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error checking status: {str(e)}")

@tasks.loop(seconds=check_interval)
async def check_accounts():
    targets = get_all_targets()
    for username, user_id in targets.items():
        try:
            status = is_account_banned(username)
            if status is None:
                continue
                
            if username not in status_cache:
                status_cache[username] = status
                continue
                
            if status_cache[username] != status:
                msg = f"🔔 @{username} is now {'BANNED ❌' if status else 'ACTIVE ✅'}"
                user = await bot.fetch_user(int(user_id))
                if user:
                    await user.send(msg)
                status_cache[username] = status
                
        except Exception as e:
            print(f"Error checking @{username}: {str(e)}")
        
        await asyncio.sleep(5)  # Small delay between checks to avoid rate limiting

if __name__ == "__main__":
    # Create scheduler for background tasks
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    scheduler.start()
    
    # Start the bot
    bot.run(DISCORD_TOKEN)
