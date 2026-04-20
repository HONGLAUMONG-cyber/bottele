import os
import telebot
from telebot import types
from datetime import datetime
import pytz

# Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    # Kênh nguồn (Up rồi xóa)
STORAGE_GROUP_ID = -1008078171493     # Nhóm lưu trữ (Giữ link vĩnh viễn)
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với **Hồng Lâu Mộng** 😊\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Hệ thống tự động lấy Link mới nhất mỗi ngày.\n"
        f"❄️ Vui lòng không chặn Bot để nhận thông báo!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", callback_data="get_link_today"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_link_today")
def handle_get_link(call):
    user_id = call.message.chat.id
    now_vn = datetime.now(VN_TZ)
    ngay_str = now_vn.strftime('%d/%m/%Y')

    try:
        # 1. Gửi thông báo đang xử lý
        status_msg = bot.send_message(user_id, f"⏳ **Đang trích xuất dữ liệu ngày {ngay_str}...**", parse_mode='Markdown')

        # 2. Tìm ID bài mới nhất từ kênh nguồn bằng cách gửi tin tạm
        temp_msg = bot.send_message(SOURCE_CHANNEL_ID, "Checking...")
        latest_id = temp_msg.message_id - 1
        bot.delete_message(SOURCE_CHANNEL_ID, temp_msg.message_id)

        # 3. Gửi bài cho người dùng
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_id=latest_id
        )

        # 4. TỰ ĐỘNG LƯU TRỮ: Copy bài đó sang nhóm lưu trữ để lưu link
        # Thêm ghi chú ngày tháng vào nhóm lưu trữ
        bot.send_message(STORAGE_GROUP_ID, f"📂 **SAO LƯU DỮ LIỆU NGÀY {ngay_str}**\n(Đã gửi cho khách: {user_id})", parse_mode='Markdown')
        bot.copy_message(
            chat_id=STORAGE_GROUP_ID,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_id=latest_id
        )

        # 5. Hoàn tất và dọn dẹp thông báo chờ
        bot.delete_message(user_id, status_msg.message_id)

    except Exception as e:
        bot.send_message(user_id, "⚠️ **Lỗi:** Không tìm thấy bài mới hoặc Bot chưa được cấp quyền Admin ở Kênh/Nhóm lưu trữ.")
        print(f"Lỗi: {e}")

bot.infinity_polling()
