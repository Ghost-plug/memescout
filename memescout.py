import threading
import time
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("8002882461:AAHmBmVaVv_F99TD1ZW301f3wp0E38BvGsA")
CHAT_ID = os.getenv(6904544779
)

# Your main bot function
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Memecoin Scout Bot is now LIVE... scanning pump.fun and gmgn.ai for 20x gems.")

def scan_gmgn():
    while True:
        try:
            response = requests.get("https://api.gmgn.ai/tokens")
            tokens = response.json()
            print("[gmgn.ai] Tokens found:", len(tokens))
            # Filtering logic here
        except Exception as e:
            print("gmgn.ai error:", e)
        time.sleep(30)

def scan_pump():
    while True:
        try:
            response = requests.get("https://pump.fun/api/trending")
            tokens = response.json()
            print("[pump.fun] Tokens found:", len(tokens))
            # Filtering logic here
        except Exception as e:
            print("pump.fun error:", e)
        time.sleep(30)

def run_parallel_scanners():
    t1 = threading.Thread(target=scan_gmgn)
    t2 = threading.Thread(target=scan_pump)
    t1.start()
    t2.start()

if __name__ == "_main_":
    run_parallel_scanners()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.run_polling()
