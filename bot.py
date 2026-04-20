import os
import telebot
from telebot import types
from datetime import datetime
import pytz

# Lấy Token an toàn từ GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Cấu hình ID và Link
SOURCE_GROUP_LINK = "https://t.me/Tramgiaitri" # Link nhóm nguồn
STORAGE_GROUP_ID = "-8078171493" # ID nhóm lưu trữ của bạn

# Thiết lập múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Chào mừng ✪ {user_name} ✪ đến với **DongBanTo** 😊\n\n"
        f"❄️ Vui lòng Đừng Chặn BOT để nhận link mới nha! ❄️"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", callback_data="get_link_today"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_link_today")
def handle_get_link(call):
    bot.answer_callback_query(call.id, "Đang trích xuất dữ liệu...")
    
    # Lấy thời gian thực tại Việt Nam
    now_vn = datetime.now(VN_TZ)
    ngay_hien_tai = now_vn.strftime("%d-%m-%Y")
    gio_hien_tai = now_vn.strftime("%H:%M:%S")
    
    response_text = (
        f"✅ **ĐÃ GỬI XONG ALBUM NGÀY {ngay_hien_tai}**\n"
        f"⏰ Thời gian: {gio_hien_tai}\n"
        f"🔥 Đã gửi xong link Tổng: 4/4 (Link)\n\n"
        f"📊 **Tình trạng lượt dùng:**\n"
        f"🎟 Còn lại: 5/5 lượt nhận link nhanh.\n"
        f"⌛ _Hệ thống tự động reset sau 30 phút!_"
    )
    
    # Tạo nút bấm chuẩn không lỗi
    sub_markup = types.InlineKeyboardMarkup()
    btn_next = types.InlineKeyboardButton(text="📅 XEM TIẾP NGÀY KHÁC", url=SOURCE_GROUP_LINK)
    btn_admin = types.InlineKeyboardButton(text="👤 HỖ TRỢ BÁO LỖI LINK", url="https://t.me/Beshanday")
    sub_markup.add(btn_next)
    sub_markup.add(btn_admin)

    # Gửi cho người dùng
    bot.send_message(call.message.chat.id, response_text, reply_markup=sub_markup, parse_mode='Markdown')

    # Tự động gửi bản sao vào nhóm lưu trữ
    archive_info = (
        f"📌 **BẢN SAO HỆ THỐNG - {ngay_hien_tai}**\n"
        f"🕒 Lúc: {gio_hien_tai}\n"
        f"👤 Khách: {call.from_user.first_name} (ID: `{call.from_user.id}`)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{response_text}"
    )
    
    try:
        bot.send_message(STORAGE_GROUP_ID, archive_info, parse_mode='Markdown')
    except Exception as e:
        print(f"Lỗi gửi lưu trữ: {e}")

bot.infinity_polling()
