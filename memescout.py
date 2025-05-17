import threading
import time
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# === CONFIGURATION ===
BOT_TOKEN           = "8002882461:AAHmBmVaVv_F99TD1ZW301f3wp0E38BvGsA"
CHAT_ID             = 6904544779
RUGCHECK_API        = "https://api.rugcheck.xyz/v1/token/{}"
MIN_LIQUIDITY_USD   = 1_000    # ignore tokens with liquidity below this
MAX_HOLDER_PERCENT  = 40       # no single wallet >10%
MIN_RUG_SCORE       = 80       # RugCheck.score ≥ 80
PUMP_CYCLE_SEC      = 30
GMGN_CYCLE_SEC      = 30

bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Track which tokens we've already alerted
seen_tokens = set()
# Flag so that /start only spins up scanning once
scanning_started = False

def send_alert(text: str):
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

def check_rug(address: str):
    """Return (is_safe: bool, score: int)."""
    try:
        res = requests.get(RUGCHECK_API.format(address), timeout=10).json()
        score = int(res.get("score", 0))
        safe  = not res.get("is_rug", True)
        return safe, score
    except Exception:
        return False, 0

def check_holders(address: str):
    """Ensure no single holder > MAX_HOLDER_PERCENT."""
    try:
        url = f"https://api.solscan.io/token/holders?token={address}&limit=10"
        data = requests.get(url, timeout=10).json().get("data", [])
        if not data:
            return False
        total = sum(h.get("amount", 0) for h in data)
        top   = max(h.get("amount", 0) for h in data)
        pct   = (top / total) * 100 if total else 100
        return pct <= MAX_HOLDER_PERCENT
    except Exception:
        return False

def scan_pumpfun():
    """Loop: fetch pump.fun → filter → alert."""
    while True:
        try:
            url = "https://pump.fun/api/project/list?sort=recent"
            projects = requests.get(url, timeout=10).json().get("projects", [])
            for p in projects:
                mint     = p.get("token", {}).get("mint")
                name     = p.get("name")
                symbol   = p.get("symbol")
                liquidity= p.get("liquidity", 0)
                link     = f"https://pump.fun/p/{p.get('id')}"

                if not mint or mint in seen_tokens:
                    continue
                if liquidity < MIN_LIQUIDITY_USD:
                    continue

                safe, score = check_rug(mint)
                if not safe or score < MIN_RUG_SCORE:
                    continue

                if not check_holders(mint):
                    continue

                # Passed all filters!
                seen_tokens.add(mint)
                msg = (
                    f"New Memecoin (pump.fun)\n\n"
                    f"Name: {name}\n"
                    f"Symbol: {symbol}\n"
                    f"Liquidity: ${liquidity}\n"
                    f"RugCheck Score: {score}\n"
                    f"[View on pump.fun]({link})"
                )
                send_alert(msg)
        except Exception as e:
            print("Pump.fun scan error:", e)
        time.sleep(PUMP_CYCLE_SEC)

def scan_gmgn():
    """Loop: fetch gmgn.ai → filter → alert."""
    while True:
        try:
            url   = "https://gmgn.ai/api/v1/listed-tokens"
            tokens= requests.get(url, timeout=10).json()
            for t in tokens:
                mint      = t.get("mint")
                name      = t.get("name")
                symbol    = t.get("symbol")
                liquidity = t.get("liquidity", 0)
                link      = f"https://gmgn.ai/token/{mint}"

                if not mint or mint in seen_tokens:
                    continue
                if liquidity < MIN_LIQUIDITY_USD:
                    continue

                safe, score = check_rug(mint)
                if not safe or score < MIN_RUG_SCORE:
                    continue

                if not check_holders(mint):
                    continue

                seen_tokens.add(mint)
                msg = (
                    f"New Memecoin (gmgn.ai)\n\n"
                    f"Name: {name}\n"
                    f"Symbol: {symbol}\n"
                    f"Liquidity: ${liquidity}\n"
                    f"RugCheck Score: {score}\n"
                    f"[View on gmgn.ai]({link})"
                )
                send_alert(msg)
        except Exception as e:
            print("gmgn.ai scan error:", e)
        time.sleep(GMGN_CYCLE_SEC)

def start_command(update: Update, context: CallbackContext):
    """Handler for /start in Telegram."""
    global scanning_started
    if scanning_started:
        update.message.reply_text("🔎 Already scanning!")
        return

    update.message.reply_text("🚀 Starting memecoin scans now!")
    # Kick off threads
    threading.Thread(target=scan_pumpfun, daemon=True).start()
    threading.Thread(target=scan_gmgn,   daemon=True).start()
    scanning_started = True

# Register handler
dispatcher.add_handler(CommandHandler("start", start_command))

if __name__ == "_main_":
    print("Bot is idle. Send /start in your Telegram chat to begin scanning.")
    updater.start_polling()
    updater.idle()