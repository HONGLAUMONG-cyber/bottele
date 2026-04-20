import os
import telebot
from telebot import types

# 1. Cấu hình Token và ID
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ

# Giao diện Chào mừng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với DongBanTo 😊\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Nhấn nút dưới đây để nhận bài mới nhất.\n"
        f"📂 Bài viết sẽ được tự động sao lưu vào nhóm lưu trữ."
    )
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🔗 LẤY FULL ALBUM HÔM NAY", callback_data="get_full_album")
    markup.add(btn)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# Xử lý lấy bài (Copy album không vết tích)
@bot.callback_query_handler(func=lambda call: call.data == "get_full_album")
def handle_get_album(call):
    user_id = call.message.chat.id
    try:
        # Thông báo chờ
        status_msg = bot.send_message(user_id, "⌛ **Đang xử lý dữ liệu sạch...**", parse_mode='Markdown')

        # Dò ID bài mới nhất
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        # Lấy 10 ID gần nhất để hốt trọn album
        message_ids = list(range(max_id - 10, max_id))

        # 1. Đẩy vào nhóm lưu trữ trước (Bản sao sạch)
        try:
            bot.copy_messages(
                chat_id=STORAGE_GROUP_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_ids=message_ids
            )
        except Exception as e:
            print(f"Lỗi lưu trữ: {e}")

        # 2. Gửi cho khách (Bản copy sạch)
        bot.copy_messages(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_ids=message_ids
        )

        bot.delete_message(user_id, status_msg.message_id)

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có bài mới hoặc chưa làm Admin ở Kênh/Nhóm.")

# Chạy Bot - Đảm bảo không lỗi cú pháp
if name == "__main__":
    bot.infinity_polling()
