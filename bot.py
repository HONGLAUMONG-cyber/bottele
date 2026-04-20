import os
import telebot
from telebot import types

# 1. Cấu hình - Lấy TOKEN từ GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ID các kênh và nhóm
SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ

# Giao diện chào mừng khi bấm /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với Hồng Lâu Mộng 😊\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Nhấn nút dưới đây để nhận Album mới nhất.\n"
        f"📂 Bài viết được sao lưu sạch (không chữ chuyển tiếp) vào nhóm."
    )
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🔗 LẤY FULL ALBUM HÔM NAY", callback_data="get_full_album")
    markup.add(btn)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# Xử lý khi nhấn nút lấy Album
@bot.callback_query_handler(func=lambda call: call.data == "get_full_album")
def handle_get_album(call):
    user_id = call.message.chat.id
    try:
        # Thông báo đang xử lý
        status_msg = bot.send_message(user_id, "⌛ **Đang copy dữ liệu sạch...**", parse_mode='Markdown')

        # Dò ID bài mới nhất bằng tin nhắn tạm
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        # Lấy danh sách 10 ID gần nhất để đảm bảo hốt trọn Album ảnh
        message_ids = list(range(max_id - 10, max_id))

        # 1. Tự động sao lưu vào nhóm lưu trữ (Bản copy sạch, không hiện 'Chuyển tiếp từ')
        try:
            bot.copy_messages(
                chat_id=STORAGE_GROUP_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_ids=message_ids
            )
        except Exception as e:
            print(f"Lỗi gửi nhóm lưu trữ: {e}")

        # 2. Gửi bản copy sạch cho người dùng
        bot.copy_messages(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_ids=message_ids
        )

        # Xóa thông báo chờ sau khi hoàn tất
        bot.delete_message(user_id, status_msg.message_id)

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có bài mới hoặc chưa được làm Admin ở Kênh/Nhóm.")

# Khởi chạy Bot - Đảm bảo cú pháp chuẩn xác với name
if name == "__main__":
    bot.infinity_polling()
