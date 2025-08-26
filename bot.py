import json
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from monitor import is_account_banned
from database import add_user, get_all_targets, load_users, save_users
from apscheduler.schedulers.background import BackgroundScheduler

with open("config.json") as f:
    config = json.load(f)

bot_token = config["bot_token"]
check_interval = config["check_interval"]
status_cache = {}

def start(update: Update, context: CallbackContext):
    welcome_message = (
        "👋 Welcome to Instagram Monitor Bot!\n"
        "\n"
        "Commands:\n"
        "/add <username> – Add a username to monitor\n"
        "/list – View your tracked usernames\n"
        "/remove <username> – Remove a tracked username\n"
        "/status <username> – Check current status of a username"
    )
    update.message.reply_text(welcome_message)

def add(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /add <instagram_username>")
        return
    username = context.args[0].strip("@").lower()
    user_id = update.message.chat_id
    add_user(user_id, username)
    update.message.reply_text(f"✅ Now monitoring @{username}")

def list_usernames(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)
    data = load_users()
    if user_id not in data or not data[user_id]["targets"]:
        update.message.reply_text("❌ You aren't tracking any usernames.")
        return
    
    targets = data[user_id]["targets"]
    msg = "📋 You are monitoring:\n" + "\n".join([f"• @{username}" for username in targets])
    update.message.reply_text(msg)

def remove(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /remove <instagram_username>")
        return
    username = context.args[0].strip("@").lower()
    user_id = str(update.message.chat_id)
    data = load_users()
    if user_id in data and username in data[user_id]["targets"]:
        data[user_id]["targets"].remove(username)
        save_users(data)
        update.message.reply_text(f"❌ Stopped monitoring @{username}")
    else:
        update.message.reply_text(f"@{username} was not being tracked.")

def status(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /status <instagram_username>")
        return
    username = context.args[0].strip("@").lower()
    result = is_account_banned(username)
    if result is None:
        update.message.reply_text("⚠️ Couldn't check status. Instagram might be blocking requests.")
    else:
        update.message.reply_text(f"@{username} is currently {'❌ BANNED' if result else '✅ ACTIVE'}")

def check_accounts():
    bot = Bot(token=bot_token)
    targets = get_all_targets()
    for username, chat_id in targets.items():
        status = is_account_banned(username)
        if status is None:
            continue
        if username not in status_cache:
            status_cache[username] = status
        if status_cache[username] != status:
            msg = f"🔔 @{username} is now {'BANNED ❌' if status else 'ACTIVE ✅'}"
            bot.send_message(chat_id=chat_id, text=msg)
            status_cache[username] = status

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", list_usernames))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("status", status))

    scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
    scheduler.add_job(check_accounts, 'interval', seconds=check_interval)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()