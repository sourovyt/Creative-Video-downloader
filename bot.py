import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import base64
import threading
from flask import Flask

# ============ CONFIG ============
BOT_TOKEN = "8574407105:AAHzlKA86eiJeKFtJKCuwE-1wIzlAycVoXY"
bot = telebot.TeleBot(BOT_TOKEN)

# ============ FORCE JOIN ============
CHANNEL_USERNAME = "@CreativeSpark1"

def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ============ FLASK KEEP ALIVE ============
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ============ START COMMAND ============
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("📢 SUBSCRIBE CHANNEL", url="https://t.me/CreativeSpark1")
    btn2 = InlineKeyboardButton("📩 CONTACT OWNER", url="https://t.me/ShahriarRazz143")
    markup.add(btn1)
    markup.add(btn2)

    text = """✨ **CREATIVE VIDEO DOWNLOADER** ✨

🚀 I can download videos from:
🔹 YouTube & YT Shorts
🔹 Instagram Reels
🔹 Facebook Videos

📌 **Just send me the link!**"""

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# ============ VIDEO HANDLER ============
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "❌ Please send a valid video link.")
        return

    if not is_joined(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"🚫 You must join our channel first to use this bot:\n\n👉 {CHANNEL_USERNAME}"
        )
        return

    status_msg = bot.reply_to(message, "🔍 Analyzing link...")

    try:
        # Optimized options for YT and others
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Prioritize MP4 for Telegram compatibility
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'max_filesize': 50000000, # 50MB Limit
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            bot.edit_message_text("⬇️ Downloading...", message.chat.id, status_msg.message_id)
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("📤 Uploading to Telegram...", message.chat.id, status_msg.message_id)

        with open(filename, 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption=f"✅ **{info.get('title', 'Video')}**\n\nPowered by: {CHANNEL_USERNAME}",
                parse_mode="Markdown"
            )

        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        error_text = str(e)
        if "File is too large" in error_text or "max_filesize" in error_text:
            bot.edit_message_text("⚠️ Video is too large! Telegram bots are limited to 50MB.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Error: {error_text[:100]}", message.chat.id, status_msg.message_id)

# ============ MAIN ============
if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    keep_alive()
    bot.infinity_polling()
