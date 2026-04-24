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

    btn1 = InlineKeyboardButton("📢 SUBSCRIBE CHANNEL", url=YOUTUBE_LINK)
    btn2 = InlineKeyboardButton("🎓 ALL TUTORIALS", url=YOUTUBE_LINK)
    btn3 = InlineKeyboardButton("📩 CONTACT OWNER", url=SUPPORT_LINK)

    markup.add(btn1)
    markup.add(btn2, btn3)

    text = """✨ *Welcome to BLACK KNOWLEDGE VIDEO DOWNLOADER* ✨

🚀 Download Instagram Reels & Facebook Videos instantly!

📌 Send a video link and I’ll handle everything.

💎 Powered by: @BLACK_KNOWLEDGE_190"""

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# ============ VIDEO HANDLER ============
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(
            message,
            "❌ Please send a valid Facebook or Instagram video link."
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

            bot.edit_message_text(
                "⬇️ Downloading... (50%)",
                message.chat.id,
                status_msg.message_id
            )

            ydl.download([url])

        bot.edit_message_text(
            "📤 Uploading... (100%)",
            message.chat.id,
            status_msg.message_id
        )

        with open(filename, 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="Downloaded Successfully! Power by: @BLACK_KNOWLEDGE_190"
            )

        # CLEANUP
        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# ============ MAIN ============
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
