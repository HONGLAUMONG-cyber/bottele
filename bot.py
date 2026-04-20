import os
import telebot
from telebot import types

# Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ (Backup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🚀 LẤY LINK MỚI NHẤT (FULL BÀI)", callback_data="get_full_post"))
    bot.send_message(message.chat.id, "Hệ thống DongBanTo đã sẵn sàng! Bấm nút để lấy toàn bộ nội dung bài mới nhất.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_full_post")
def handle_get_post(call):
    user_id = call.message.chat.id
    try:
        # Gửi tin nhắn tạm để dò ID
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        # Quét lấy 5 tin nhắn gần nhất (để đảm bảo lấy đủ 1 bài gồm nhiều ảnh/text)
        found = False
        for i in range(max_id - 1, max_id - 6, -1):
            try:
                # 1. Copy cho khách
                bot.copy_message(chat_id=user_id, from_chat_id=SOURCE_CHANNEL_ID, message_id=i)
                # 2. Sao lưu luôn vào nhóm lưu trữ
                bot.copy_message(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_id=i)
                found = True
            except:
                continue
        
        if not found:
            bot.send_message(user_id, "Kênh nguồn đang trống, hãy đăng bài rồi thử lại nhé!")

    except Exception as e:
        bot.send_message(user_id, "Lỗi rồi đại ca ơi! Kiểm tra lại quyền Admin của Bot nhé.")

bot.infinity_polling()
