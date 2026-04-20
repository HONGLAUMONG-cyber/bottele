import os
import telebot
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ (Phải thêm Bot làm Admin ở đây)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔗 LẤY FULL ALBUM HÔM NAY", callback_data="get_full_album"))
    
    welcome_text = (
        f"Chào mừng ✪ {message.from_user.first_name} ✪ đến với DongBanTo 😊\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Nhấn nút dưới đây để nhận toàn bộ Album mới nhất.\n"
        f"📂 Dữ liệu sẽ được tự động sao lưu vào kho lưu trữ!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_full_album")
def handle_get_album(call):
    user_id = call.message.chat.id
    try:
        # Gửi thông báo chờ
        status_msg = bot.send_message(user_id, "⌛ **Đang trích xuất và sao lưu Album...**", parse_mode='Markdown')

        # Dò ID mới nhất bằng tin nhắn tạm
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        # Lấy danh sách ID của các tin nhắn gần nhất (thường 1 album có tối đa 10 ảnh)
        # Chúng ta lấy 10 ID gần nhất để không sót ảnh nào
        message_ids = list(range(max_id - 10, max_id))

        # 2. SAO LƯU VÀO NHÓM LƯU TRỮ TRƯỚC
        try:
            bot.forward_messages(
                chat_id=STORAGE_GROUP_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_ids=message_ids
            )
            bot.send_message(STORAGE_GROUP_ID, f"✅ Đã sao lưu bài viết cho khách: `{user_id}`", parse_mode='Markdown')
        except Exception as e:
            print(f"Lỗi sao lưu: {e}")

        # 3. GỬI CHO NGƯỜI DÙNG (Dùng forward_messages để giữ nguyên Album)
        bot.forward_messages(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_ids=message_ids
        )

        # Dọn dẹp thông báo chờ
        bot.delete_message(user_id, status_msg.message_id)

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi hệ thống! Hãy chắc chắn Bot là Admin của cả Kênh và Nhóm lưu trữ.")
        # Báo lỗi về nhóm lưu trữ để bạn theo dõi
        bot.send_message(STORAGE_GROUP_ID, f"⚠️ Bot gặp lỗi khi xử lý bài viết: {str(e)}")

bot.infinity_polling()
