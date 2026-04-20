import os
import telebot
import uuid # Dùng để tạo mã link ngẫu nhiên
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot" # Thay đúng username bot của bạn

# Lưu trữ tạm thời link (Trong thực tế nên dùng Database)
link_storage = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    # Nếu khách bấm vào link có mã (ví dụ: /start batch_abcd)
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            # Nhả bài ra cho khách
            bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
        else:
            bot.send_message(message.chat.id, "❌ Link đã hết hạn hoặc không tồn tại.")
    else:
        # Giao diện chào mừng bình thường
        welcome_text = f"Chào mừng ✪ {message.from_user.first_name} ✪\n✨ Bấm nút để lấy link bài mới nhất."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK ALBUM", callback_data="get_link"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        # Dò ID bài mới nhất
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)
        
        # Lấy dải 10 ID (Album/Video)
        message_ids = list(range(max_id - 10, max_id))

        # 1. Sao lưu vào nhóm lưu trữ trước
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except: pass

        # 2. Tạo mã link ngẫu nhiên
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = message_ids # Lưu danh sách ID vào bộ nhớ

        # 3. Gửi link cho người dùng
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        bot.send_message(user_id, f"✅ Đã tạo link thành công!\n\n🔗 Link của bạn:\n`{share_link}`", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có quyền Admin.")

if __name__ == "__main__":
    bot.infinity_polling()
