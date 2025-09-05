# import discord
# import asyncio
# import json
# import aiohttp
# import logging
# from discord.ext import tasks, commands

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger('instagram_tracker')

# TOKEN removed (use DISCORD_BOT_TOKEN from environment instead)
# # Removed CHANNEL_ID since we'll use DMs instead

# intents = discord.Intents.default()
# intents.message_content = True
# bot = commands.Bot(command_prefix="!", intents=intents)

# @bot.event
# async def on_ready():
#     print(f"Logged in as {bot.user}")
#     try:
#         synced = await bot.tree.sync()
#         print(f"Synced {len(synced)} command(s)")
#     except Exception as e:
#         print(f"Error syncing commands: {e}")
#     check_instagram.start()

# def load_data():
#     try:
#         with open("data.json", "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {}

# def save_data(data):
#     with open("data.json", "w") as f:
#         json.dump(data, f, indent=2)

# async def fetch_instagram_data(session, username):
#     url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "X-IG-App-ID": "936619743392459"  # This is a public ID used by Instagram's web client
#     }
    
#     try:
#         logger.info(f"Fetching data for @{username}")
#         async with session.get(url, headers=headers) as resp:
#             if resp.status == 200:
#                 data = await resp.json()
#                 if 'data' not in data or 'user' not in data['data']:
#                     return None
                    
#                 user_data = data['data']['user']
#                 return {
#                     "username": user_data.get("username"),
#                     "full_name": user_data.get("full_name", ""),
#                     "is_verified": user_data.get("is_verified", False),
#                     "profile_pic_url": user_data.get("profile_pic_url_hd", ""),
#                     "bio": user_data.get("biography", ""),
#                     "followers": user_data.get("edge_follow", {}).get("count", 0)
#                 }
#             elif resp.status == 404:
#                 return {"status": "not_found"}
#             else:
#                 logger.warning(f"Unexpected status code {resp.status} for @{username}")
#                 return None
#     except Exception as e:
#         logger.error(f"Error fetching data for @{username}: {str(e)}")
#         return None

# def build_embed(title, description, user_data, color):
#     embed = discord.Embed(title=title, description=description, color=color)
#     embed.set_thumbnail(url=user_data.get("profile_pic_url", ""))
#     embed.add_field(name="Username", value=f"@{user_data.get('username', 'unknown')}", inline=True)
#     embed.add_field(name="Full Name", value=user_data.get("full_name", "N/A"), inline=True)
#     if user_data.get("bio"):
#         embed.add_field(name="Bio", value=user_data["bio"], inline=False)
#     embed.add_field(name="Followers", value=f"{user_data.get('followers', 0):,}", inline=True)
#     return embed

 

# @bot.tree.command(name="adduser", description="Start tracking an Instagram username.")
# async def add_user(interaction: discord.Interaction, username: str):
#     await interaction.response.defer()  # Tell Discord we're working on it
    
#     username = username.lower()
#     data = load_data()
    
#     if username in data:
#         await interaction.followup.send(f"`@{username}` is already being tracked.")
#         return
        
#     # Check if username exists on Instagram
#     try:
#         async with aiohttp.ClientSession() as session:
#             # First try the web profile API
#             url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
#             headers = {
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#                 "X-IG-App-ID": "936619743392459"
#             }
            
#             async with session.get(url, headers=headers) as resp:
#                 if resp.status == 404:
#                     await interaction.followup.send(f"❌ Instagram user `@{username}` doesn't exist.")
#                     return
#                 elif resp.status != 200:
#                     await interaction.followup.send(f"⚠️ Couldn't verify Instagram user right now. Please try again in a few minutes.")
#                     logger.warning(f"Instagram API returned status {resp.status} for @{username}")
#                     return
                
#                 # Parse the response
#                 user_data = await resp.json()
#                 if 'data' not in user_data or 'user' not in user_data['data']:
#                     await interaction.followup.send("❌ Couldn't process Instagram's response. The service might be temporarily unavailable.")
#                     return
                    
#                 user_info = user_data['data']['user']
#                 followers = user_info.get('edge_follow', {}).get('count', 0)
                
#                 # Store the username with initial data
#                 data[username] = {
#                     "added_by": str(interaction.user.id),
#                     "followers": followers,
#                     "is_verified": user_info.get('is_verified', False),
#                     "profile_pic_url": user_info.get('profile_pic_url_hd', '')
#                 }
#                 save_data(data)
                
#                 await interaction.followup.send(
#                     f"✅ Now tracking `@{username}` with {followers:,} followers. "
#                     f"You'll receive updates via DM."
#                 )
                
#     except Exception as e:
#         logger.error(f"Error adding user @{username}: {str(e)}")
#         await interaction.followup.send("❌ An error occurred while adding this user. Please try again later.")

# @bot.tree.command(name="removeuser", description="Stop tracking an Instagram username.")
# async def remove_user(interaction: discord.Interaction, username: str):
#     data = load_data()
#     if username.lower() not in data:
#         await interaction.response.send_message(f"`@{username}` is not being tracked.")
#     else:
#         del data[username.lower()]
#         save_data(data)
#         await interaction.response.send_message(f"❌ Stopped tracking `@{username}`.")

# @bot.tree.command(name="listusers", description="List all tracked Instagram usernames.")
# async def list_users(interaction: discord.Interaction):
#     data = load_data()
#     if not data:
#         await interaction.response.send_message("No users are currently being tracked.")
#     else:
#         tracked = "\n".join(f"@{u}" for u in data)
#         await interaction.response.send_message(f"📋 Currently tracking:\n{tracked}")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if message.content.startswith("!watch "):
#         username = message.content.split("!watch ")[1].strip().lower()
#         data = load_data()
#         if username in data:
#             await message.channel.send(f"`@{username}` is already being tracked.")
#         else:
#             data[username] = {}
#             save_data(data)
#             await message.channel.send(f"✅ Now tracking `@{username}`.")

# @tasks.loop(minutes=1)  # Changed to 1 minute for testing
# async def check_instagram():
#     logger.info("Starting Instagram check...")
#     await bot.wait_until_ready()
#     old_data = load_data()
#     async with aiohttp.ClientSession() as session:
#         for user in list(old_data.keys()):
#             current_data = await fetch_instagram_data(session, user)
#             if current_data is None:
#                 logger.warning(f"Failed to fetch data for @{user}")
#                 continue
                
#             # Get the user who added this account
#             added_by = old_data[user].get("added_by")
#             if not added_by:
#                 logger.warning(f"No added_by found for @{user}")
#                 continue
                
#             try:
#                 user_obj = await bot.fetch_user(int(added_by))
#                 if not user_obj:
#                     continue
                    
#                 if current_data.get("status") == "not_found":
#                     if old_data[user].get("status") != "not_found":
#                         embed = discord.Embed(
#                             title="⚠️ Account Offline",
#                             description=f"Instagram user `@{user}` seems to be removed or deactivated.",
#                             color=discord.Color.red()
#                         )
#                         await user_obj.send(embed=embed)
#                         old_data[user] = {"status": "not_found", "added_by": added_by}
#                         save_data(old_data)
#                     continue

#                 if old_data[user].get("status") == "not_found":
#                     embed = build_embed("✅ Account Online", f"`@{user}` is now back online.", current_data, discord.Color.green())
#                     await user_obj.send(embed=embed)
#             except Exception as e:
#                 print(f"Error sending DM to user {added_by}: {e}")

#             prev = old_data[user]
#             if "is_verified" in prev and prev["is_verified"] != current_data["is_verified"]:
#                 if current_data["is_verified"]:
#                     embed = build_embed("🔵 Verified!", f"`@{user}` just got **verified**!", current_data, discord.Color.blue())
#                 else:
#                     embed = build_embed("⚪ Unverified", f"`@{user}` is no longer verified.", current_data, discord.Color.light_grey())
#                 await channel.send(embed=embed)

#             if "followers" in prev and prev.get("followers") != current_data.get("followers"):
#                 diff = current_data["followers"] - prev.get("followers", 0)
#                 emoji = "📈" if diff > 0 else "📉"
#                 change_text = f"{emoji} `@{user}` follower count changed: {prev.get('followers', 0):,} → {current_data['followers']:,} ({diff:+,})"
#                 embed = build_embed("👥 Follower Change", change_text, current_data, discord.Color.purple())
#                 await user_obj.send(embed=embed)

#             # Preserve the added_by information
#             current_data["added_by"] = added_by
#             old_data[user] = current_data
#             save_data(old_data)

# bot.run(TOKEN)


import discord
import asyncio
import json
import aiohttp
from aiohttp import web
import logging
import os
from datetime import datetime
from discord.ext import tasks, commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment setup - USE .env FILE FOR SECURITY
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Discord bot token
SESSION_ID = os.getenv("INSTAGRAM_SESSION_ID")  # From dummy IG account

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("instagram_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('instagram_tracker')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Instagram API configuration
INSTAGRAM_HEADERS = {
    "User-Agent": USER_AGENT,
    "X-IG-App-ID": "936619743392459",
    "Cookie": f"sessionid={SESSION_ID};"
}

# --- Persistent data storage configuration ---
# Prefer a persistent directory if available (e.g., Render persistent disk at /var/data).
# Falls back to a local hidden folder inside the container or repo when not provided.
RENDER_HINT = os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("RENDER_INSTANCE_ID")
DEFAULT_DATA_DIR = "/var/data" if RENDER_HINT else os.path.join(".", ".localdata")
DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
DATA_FILE = os.path.join(DATA_DIR, "data.json")

def _ensure_data_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create data dir {DATA_DIR}: {e}")

def _migrate_legacy_file():
    """If legacy ./data.json exists and persistent file doesn't, migrate once."""
    legacy_path = os.path.join(".", "data.json")
    if os.path.exists(legacy_path) and not os.path.exists(DATA_FILE):
        try:
            with open(legacy_path, "r") as f:
                raw = f.read()
            # Validate JSON before migrating
            _ = json.loads(raw)
            with open(DATA_FILE, "w") as f:
                f.write(raw)
            logger.info(f"Migrated legacy data from {legacy_path} to {DATA_FILE}")
        except Exception as e:
            logger.warning(f"Could not migrate legacy data.json: {e}")

_ensure_data_dir()
_migrate_legacy_file()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Command sync error: {e}")
    check_instagram.start()

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Check for old format and migrate in-memory
            if "users" not in data:
                logger.info("Old data format detected. Migrating to new structure.")
                return {"users": data, "meta": {"last_checked": ""}}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "meta": {"last_checked": ""}}

def save_data(data):
    data["meta"]["last_checked"] = datetime.utcnow().isoformat()
    tmp_path = DATA_FILE + ".tmp"
    try:
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except Exception as e:
        logger.error(f"Failed to save data atomically to {DATA_FILE}: {e}")

async def fetch_instagram_data(session, username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        logger.info(f"Fetching: @{username}")
        async with session.get(url, headers=INSTAGRAM_HEADERS) as resp:
            if resp.status == 403:
                logger.critical("SESSION EXPIRED! Update Instagram session ID")
                return "session_expired"
            elif resp.status == 429:
                logger.warning("RATE LIMITED - slowing down requests")
                await asyncio.sleep(60)
                return "rate_limited"
            elif resp.status == 404:
                return "not_found"
            elif resp.status != 200:
                logger.warning(f"Status {resp.status} for @{username}")
                return None
                
            data = await resp.json()
            if not data.get('data') or not data['data'].get('user'):
                return None
                
            user = data['data']['user']
            return {
                "username": user.get("username"),
                "full_name": user.get("full_name", ""),
                "is_verified": user.get("is_verified", False),
                "profile_pic_url": user.get("profile_pic_url_hd", ""),
                "bio": user.get("biography", ""),
                # Correct field: followers are in edge_followed_by; edge_follow is 'following'
                "followers": user.get("edge_followed_by", {}).get("count", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

def build_embed(title, description, user_data, color):
    embed = discord.Embed(title=title, description=description, color=color)
    if user_data.get("profile_pic_url"):
        embed.set_thumbnail(url=user_data["profile_pic_url"])
    embed.add_field(name="👤 Username", value=f"@{user_data.get('username', '?')}", inline=True)
    embed.add_field(name="📛 Full Name", value=user_data.get("full_name", "N/A"), inline=True)
    if user_data.get("bio"):
        embed.add_field(name="📝 Bio", value=user_data["bio"][:500] + "..." if len(user_data["bio"]) > 500 else user_data["bio"], inline=False)
    embed.add_field(name="👥 Followers", value=f"{user_data.get('followers', 0):,}", inline=True)
    embed.set_footer(text=f"Tracked by Instagram Tracker • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    return embed

# --- Minimal HTTP server for Render Web Service ---
async def health_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})

async def start_http_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/healthz", health_handler)
    app.router.add_get("/", health_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"HTTP health server started on port {port}")
    return runner

@bot.tree.command(name="adduser", description="Start tracking an Instagram account")
async def add_user(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    username = username.lower()
    data = load_data()
    
    if username in data["users"]:
        await interaction.followup.send(f"⚠️ `@{username}` is already being tracked.", ephemeral=True)
        return
        
    async with aiohttp.ClientSession() as session:
        user_data = await fetch_instagram_data(session, username)
        
        if user_data == "session_expired":
            await interaction.followup.send("🔒 Session expired! Contact bot administrator.", ephemeral=True)
            return
        elif not user_data:
            await interaction.followup.send(f"❌ Failed to fetch @{username}. Account may be private or invalid.", ephemeral=True)
            return
        elif user_data == "not_found":
            await interaction.followup.send(f"❌ Instagram user `@{username}` doesn't exist.", ephemeral=True)
            return
            
        # Store user data
        data["users"][username] = {
            "added_by": str(interaction.user.id),
            "added_at": datetime.utcnow().isoformat(),
            "followers": user_data["followers"],
            "is_verified": user_data["is_verified"],
            "bio": user_data["bio"],
            "profile_pic_url": user_data["profile_pic_url"],
            "last_checked": datetime.utcnow().isoformat()
        }
        save_data(data)
        
        embed = build_embed(
            "✅ Tracking Started", 
            f"Now monitoring @{username}", 
            user_data, 
            discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        
        # Send confirmation DM
        try:
            user = await bot.fetch_user(interaction.user.id)
            await user.send(f"🔔 You'll receive updates for @{username} in DMs")
        except discord.Forbidden:
            logger.warning(f"Couldn't DM user {interaction.user.id}")

@bot.tree.command(name="removeuser", description="Stop tracking an Instagram account")
async def remove_user(interaction: discord.Interaction, username: str):
    username = username.lower()
    data = load_data()
    
    if username not in data["users"]:
        await interaction.response.send_message(
            f"❌ `@{username}` is not being tracked.",
            ephemeral=True
        )
        return
        
    # Get user who added for notification
    added_by = data["users"][username]["added_by"]
    del data["users"][username]
    save_data(data)
    
    # Send confirmation
    await interaction.response.send_message(
        f"❌ Stopped tracking `@{username}`",
        ephemeral=True
    )
    
    # Notify original adder
    try:
        user = await bot.fetch_user(int(added_by))
        await user.send(f"🚫 No longer tracking @{username}")
    except (discord.NotFound, discord.Forbidden):
        pass

@bot.tree.command(name="listusers", description="Show all tracked accounts")
async def list_users(interaction: discord.Interaction):
    data = load_data()
    if not data["users"]:
        await interaction.response.send_message(
            "📭 No accounts being tracked",
            ephemeral=True
        )
        return
        
    embed = discord.Embed(
        title="📋 Tracked Instagram Accounts",
        color=discord.Color.blurple()
    )
    
    for i, (username, info) in enumerate(data["users"].items(), 1):
        added_by = await bot.fetch_user(int(info["added_by"]))
        embed.add_field(
            name=f"{i}. @{username}",
            value=f"Added by: {added_by.display_name}\nFollowers: {info['followers']:,}",
            inline=False
        )
    
    embed.set_footer(text=f"Total tracked: {len(data['users'])} accounts")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="userinfo", description="Show current account info")
async def user_info(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    username = username.lower()
    data = load_data()
    
    async with aiohttp.ClientSession() as session:
        user_data = await fetch_instagram_data(session, username)
        
        if not user_data or isinstance(user_data, str):
            await interaction.followup.send(f"❌ Couldn't fetch @{username}")
            return
            
        embed = build_embed(
            "ℹ️ Account Information", 
            f"Current stats for @{username}", 
            user_data, 
            discord.Color.blue()
        )
        
        # Add verification status
        embed.add_field(
            name="🔰 Verification", 
            value="Verified ✅" if user_data["is_verified"] else "Not verified ❌", 
            inline=True
        )
        
        # Add tracking status if applicable
        if username in data["users"]:
            last_checked = datetime.fromisoformat(data["users"][username]["last_checked"])
            embed.add_field(
                name="📊 Tracking Status", 
                value=f"Tracked since {last_checked.strftime('%Y-%m-%d')}",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)

@tasks.loop(minutes=5)
async def check_instagram():
    logger.info("Starting account checks...")
    data = load_data()
    if not data["users"]:
        return
        
    async with aiohttp.ClientSession() as session:
        for i, (username, user_data) in enumerate(data["users"].items()):
            # Rate limit protection
            if i > 0:
                await asyncio.sleep(10)  # 10s between requests
            
            try:
                current = await fetch_instagram_data(session, username)
                
                # Skip failed checks
                if not current or isinstance(current, str):
                    continue
                    
                # 1. Check if account was reactivated
                if user_data.get("status") == "not_found":
                    data["users"][username].pop("status", None)
                    save_data(data)
                    await notify_user(
                        user_data["added_by"],
                        build_embed(
                            "✅ Account Reactivated",
                            f"@{username} is back online",
                            current,
                            discord.Color.green()
                        )
                    )
                
                # 2. Verify account status
                if current == "not_found":
                    if user_data.get("status") != "not_found":
                        data["users"][username]["status"] = "not_found"
                        save_data(data)
                        await notify_user(
                            user_data["added_by"],
                            build_embed(
                                "⚠️ Account Unavailable",
                                f"@{username} was deleted or deactivated",
                                user_data,
                                discord.Color.red()
                            )
                        )
                    continue
                
                # --- Start of change detection ---
                something_changed = False

                # 3. Check verification status
                if user_data.get("is_verified") != current.get("is_verified"):
                    something_changed = True
                    data["users"][username]["is_verified"] = current["is_verified"]
                    await notify_user(
                        user_data["added_by"],
                        build_embed(
                            "🔰 Verification Change",
                            f"@{username} is now {'VERIFIED' if current['is_verified'] else 'UNVERIFIED'}",
                            current,
                            discord.Color.gold() if current['is_verified'] else discord.Color.light_grey()
                        )
                    )
                
                # 4. Check follower changes
                old_followers = user_data.get("followers", 0)
                new_followers = current.get("followers", 0)
                
                if old_followers != new_followers:
                    something_changed = True
                    diff = new_followers - old_followers
                    data["users"][username]["followers"] = new_followers
                    await notify_user(
                        user_data["added_by"],
                        build_embed(
                            "📈 Follower Update",
                            f"`{diff:+,}` change since last check",
                            current,
                            discord.Color.purple()
                        )
                    )

                # 5. Check bio changes
                old_bio = user_data.get("bio", "")
                new_bio = current.get("bio", "")

                if old_bio != new_bio:
                    something_changed = True
                    data["users"][username]["bio"] = new_bio
                    
                    bio_embed = discord.Embed(
                        title="📝 Bio Changed",
                        description=f"The bio for @{username} has been updated.",
                        color=discord.Color.orange()
                    )
                    bio_embed.add_field(name="Old Bio", value=(old_bio or "N/A")[:1024], inline=False)
                    bio_embed.add_field(name="New Bio", value=(new_bio or "N/A")[:1024], inline=False)
                    if current.get("profile_pic_url"):
                        bio_embed.set_thumbnail(url=current["profile_pic_url"])
                    bio_embed.set_footer(text=f"Tracked by Instagram Tracker • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

                    await notify_user(user_data["added_by"], bio_embed)

                # --- End of change detection ---

                # Finally, update the last checked timestamp and save if needed
                data["users"][username]["last_checked"] = datetime.utcnow().isoformat()
                if something_changed:
                    save_data(data)
                    
            except Exception as e:
                logger.error(f"Error processing @{username}: {str(e)}")

async def notify_user(user_id, embed):
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(embed=embed)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
        logger.warning(f"Couldn't notify user {user_id}: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f"Command error: {str(error)}")

async def main():
    if not TOKEN or not SESSION_ID:
        logger.critical("Missing environment variables! Check DISCORD_BOT_TOKEN and INSTAGRAM_SESSION_ID")
        return

    runner = await start_http_server()
    try:
        await bot.start(TOKEN)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")