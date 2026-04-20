import os
import telebot
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1003842996683     # ID nhóm lưu trữ mới của bạn

# Giao diện chào mừng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với **DongBanTo** 😊\n"
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
        # Dò ID bài mới nhất
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        # Lấy dải 100 ID gần nhất
        message_ids = list(range(max_id - 10, max_id))

        # 1. Gửi vào NHÓM LƯU TRỮ (Dùng copy_messages để giữ nguyên Album)
        try:
            bot.copy_messages(
                chat_id=-1003842996683, 
                from_chat_id=SOURCE_CHANNEL_ID, 
                message_ids=message_ids
            )
        except:
            pass

        # 2. Gửi cho KHÁCH HÀNG (Dùng copy_messages để giữ nguyên Album)
        bot.copy_messages(
            chat_id=user_id, 
            from_chat_id=SOURCE_CHANNEL_ID, 
            message_ids=message_ids
        )

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có quyền Admin hoặc dải ID trống.")

# KHỞI CHẠY BOT - ĐÃ KIỂM TRA CÚ PHÁP CHUẨN
if __name__ == "__main__":
    bot.infinity_polling()
