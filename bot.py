import os
import telebot
from telebot import types
from datetime import datetime
import pytz

# Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔗 LẤY TẤT CẢ LINK HÔM NAY", callback_data="get_all_today"))
    bot.send_message(
        message.chat.id, 
        f"Chào mừng bạn! Nhấn nút dưới đây để lấy toàn bộ danh sách link mới nhất ngày hôm nay.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "get_all_today")
def handle_get_all(call):
    user_id = call.message.chat.id
    now_vn = datetime.now(VN_TZ)
    start_of_day = now_vn.replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        status_msg = bot.send_message(user_id, "⏳ **Đang quét toàn bộ dữ liệu hôm nay...**", parse_mode='Markdown')

        # Dò ID bài viết mới nhất
        temp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
        current_max_id = temp_msg.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, current_max_id)

        found_any = False
        # Quét ngược từ tin mới nhất về trước (trong phạm vi 50 tin nhắn gần nhất để tránh treo)
        for msg_id in range(current_max_id - 1, current_max_id - 51, -1):
            try:
                # Forward thử để kiểm tra nội dung
                forwarded = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, msg_id, disable_notification=True)
                
                # Kiểm tra xem tin nhắn có phải trong ngày hôm nay không
                msg_date = datetime.fromtimestamp(forwarded.date, VN_TZ)
                
                if msg_date >= start_of_day:
                    # Nếu đúng hôm nay, copy sang cho người dùng
                    bot.copy_message(chat_id=user_id, from_chat_id=SOURCE_CHANNEL_ID, message_id=msg_id)
                    found_any = True
                else:
                    # Nếu đã quét đến tin của ngày hôm qua thì dừng lại
                    bot.delete_message(STORAGE_GROUP_ID, forwarded.message_id)
                    break
            except Exception:
                continue

        bot.delete_message(user_id, status_msg.message_id)

        if not found_any:
            bot.send_message(user_id, "⚠️ Hôm nay Admin chưa đăng bài nào mới.")
        else:
            bot.send_message(user_id, "✅ Đã gửi toàn bộ nội dung trong ngày cho bạn!")

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi hệ thống: Bot cần quyền Admin ở cả Kênh và Nhóm lưu trữ.")

bot.infinity_polling()
