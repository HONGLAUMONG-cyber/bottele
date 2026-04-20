import os
import telebot
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1008078171493     

# Giao diện chào mừng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với DongBanTo 😊\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Nhấn nút dưới đây để nhận Album mới nhất.\n"
        f"📂 Bài viết được sao lưu sạch (không chữ chuyển tiếp) vào nhóm."
    )
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🔗 LẤY FULL ALBUM HÔM NAY", callback_data="get_full_album")
    markup.add(btn)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# Xử lý lấy Album sạch
@bot.callback_query_handler(func=lambda call: call.data == "get_full_album")
def handle_get_album(call):
    user_id = call.message.chat.id
    try:
        status_msg = bot.send_message(user_id, "⌛ **Đang xử lý dữ liệu sạch...**", parse_mode='Markdown')
        
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        message_ids = list(range(max_id - 10, max_id))

        # 1. Sao lưu nhóm (Sạch 100%)
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except:
            pass

        # 2. Gửi cho khách (Sạch 100%)
        bot.copy_messages(chat_id=user_id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)

        bot.delete_message(user_id, status_msg.message_id)
    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có bài mới hoặc chưa được cấp quyền Admin.")

# DÒNG NÀY CỰC KỲ QUAN TRỌNG - PHẢI CÓ ĐỦ 2 DẤU GẠCH DƯỚI __
if name == "__main__":
    bot.infinity_polling()
