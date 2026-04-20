import os
import telebot
import time

# Lấy Token từ môi trường hệ thống (GitHub Secrets)
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Kiểm tra xem Token có tồn tại không để tránh lỗi treo bot
if not TOKEN:
    print("Lỗi: Không tìm thấy TELEGRAM_TOKEN trong Secrets!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Lệnh /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ **Chào mừng bạn đến với Hồng Lâu Mộng Bot!** ✨\n\n"
        "Bot đang chạy ổn định trên GitHub Actions.\n"
        "Các lệnh hiện có:\n"
        "/start - Khởi động bot\n"
        "/id - Xem ID Telegram của bạn\n"
        "/info - Xem thông tin hệ thống"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Lệnh /id - Rất cần thiết để bạn quản trị bot
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 ID của bạn là: `{message.from_user.id}`", parse_mode='Markdown')

# Phản hồi tin nhắn văn bản thông thường
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_text = message.text
    bot.reply_to(message, f"Bot đã nhận được tin nhắn: *{user_text}*", parse_mode='Markdown')

# Chạy bot liên tục
print("Bot đang bắt đầu chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
