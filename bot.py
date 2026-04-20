import os
import telebot
from telebot import types
from datetime import datetime
import pytz # Thư viện xử lý múi giờ

# Lấy Token từ GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Cấu hình ID
SOURCE_GROUP_LINK = "https://t.me/+VvIUmvGS8C4yMGNl"
STORAGE_GROUP_ID = "-8078171493" 

# Thiết lập múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với **Hồng Lâu Mộng** 😊\n\n"
        f"❄️ Vui lòng Đừng Chặn BOT để nhận link mới nha! ❄️"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", callback_data="get_link_today"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_link_today")
def handle_get_link(call):
    bot.answer_callback_query(call.id, "Đang lấy dữ liệu thời gian thực...")
    
    # Lấy ngày và giờ hiện tại tại Việt Nam
    now_vn = datetime.now(VN_TZ)
    ngay_hien_tai = now_vn.strftime("%d-%m-%Y")
    gio_hien_tai = now_vn.strftime("%H:%M:%S")
    
    # Nội dung gửi cho khách (Cập nhật ngày giờ động)
    response_text = (
        f"✅ **ĐÃ GỬI XONG ALBUM NGÀY {ngay_hien_tai}**\n"
        f"⏰ Thời gian: {gio_hien_tai}\n"
        f"🔥 Đã gửi xong link Tổng: 4/4 (Link)\n\n"
        f"📊 **Tình trạng lượt dùng:**\n"
        f"🎟 Còn lại: 5/5 lượt nhận link nhanh.\n"
        f"⌛ _Hệ thống tự động cập nhật lúc: {gio_hien_tai}_"
    )
    
    sub_markup = types.InlineKeyboardMarkup()
    sub_markup.add(types.InlineKeyboardButton("📅 XEM TIẾP NGÀY KHÁC", url=https://t.me/Tramgiaitri))
    sub_markup.add(types.InlineKeyboardButton("👤 HỖ TRỢ BÁO LỖI LINK", url="https://t.me/Beshanday"))

    # Gửi cho khách
    bot.send_message(call.message.chat.id, response_text, reply_markup=sub_markup, parse_mode='Markdown')

    # Gửi lưu trữ vào nhóm (kèm thông tin thời gian chính xác)
    archive_info = (
        f"📌 **LOG HỆ THỐNG - {ngay_hien_tai}**\n"
        f"🕒 Lúc: {gio_hien_tai}\n"
        f"👤 Khách: {call.from_user.first_name} (`{call.from_user.id}`)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{response_text}"
    )
    
    try:
        bot.send_message(STORAGE_GROUP_ID, archive_info, parse_mode='Markdown')
    except Exception as e:
        print(f"Lỗi lưu trữ: {e}")

bot.infinity_polling()    bot.reply_to(message, f"Bot đã nhận được tin nhắn: *{user_text}*", parse_mode='Markdown')

# Chạy bot liên tục
print("Bot đang bắt đầu chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
