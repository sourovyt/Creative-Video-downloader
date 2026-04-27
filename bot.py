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

# ============ SECURED LINKS ============
YOUTUBE_LINK = base64.b64decode(
    "aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE="
).decode()

SUPPORT_LINK = base64.b64decode(
    "aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA="
).decode()

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
    btn2 = InlineKeyboardButton("🎓 ALL TUTORIALS", url="https://youtube.com/@creativesparksociety?si=sOBu86XaQ4ZpP9IK")
    btn3 = InlineKeyboardButton("📩 CONTACT OWNER", url="https://t.me/ShahriarRazz143")

    markup.add(btn1)
    markup.add(btn2, btn3)

    text = """✨ Welcome to CREATIVE VIDEO DOWNLOADER ✨

🚀 Download Instagram Reels & Facebook Videos instantly!

📌 Send a video link and I’ll handle everything.

💎 Powered by: @CreativeDownloader_Bot"""

    bot.send_message(message.chat.id, text, reply_markup=markup)

# ============ VIDEO HANDLER ============
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "❌ Please send a valid Facebook or Instagram video link.")
        return

    # 🚫 FORCE JOIN CHECK
    if not is_joined(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🚫 You must join our channel first to use this bot:\n\n"
            "👉 https://t.me/CreativeSpark1"
        )
        return

    try:
        status_msg = bot.reply_to(message, "🔍 Analyzing...")

        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)

            bot.edit_message_text("⬇️ Downloading... (50%)", message.chat.id, status_msg.message_id)

            ydl.download([url])

        bot.edit_message_text("📤 Uploading... (100%)", message.chat.id, status_msg.message_id)

        with open(filename, 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="Downloaded Successfully! Power by: @CreativeSpark1"
            )

        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# ============ MAIN ============
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
