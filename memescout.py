import os
import threading
import time
import requests
from telegram import Update, Bot
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
from dotenv import load_dotenv

# Load environment variables from Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = str(os.getenv("CHAT_ID"))  # Ensure it's a string

# Globals
bot_running = False

# Define a simple token scoring function (you can expand it)
def score_token(token_data):
    if (
        token_data.get("rugcheck_safe", False)
        and token_data.get("top_holder_percent", 100) <= 10
        and token_data.get("source") in ["pump.fun", "gmgn.ai"]
    ):
        return True
    return False

# Mock function to simulate scanning tokens
def scan_tokens():
    while bot_running:
        print("[Scanner] Checking tokens...")
        time.sleep(15)  # Simulate waiting between scans

        # Mock result
        mock_token = {
            "name": "SampleCoin",
            "rugcheck_safe": True,
            "top_holder_percent": 9.4,
            "source": "pump.fun",
            "url": "https://pump.fun/samplecoin"
        }

        if score_token(mock_token):
            message = (
                f"Token: {mock_token['name']}\n"
                f"Source: {mock_token['source']}\n"
                f"Top Holder: {mock_token['top_holder_percent']}%\n"
                f"RugCheck: SAFE\n"
                f"Link: {mock_token['url']}"
            )
            print(f"[Scanner] Sending to Telegram: {message}")
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=CHAT_ID, text=message)

# Start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_running
    if not bot_running:
        bot_running = True
        await update.message.reply_text("Memecoin Scout Bot activated! Scanning for 20x potential tokens...")
        threading.Thread(target=scan_tokens).start()
    else:
        await update.message.reply_text("Bot is already running!")

# Main application setup
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    print("[System] Telegram bot is live. Use /start to activate scanning.")
    await app.run_polling()

# Entrypoint
if __name__ == "_main_":
    import asyncio
    asyncio.run(main())
