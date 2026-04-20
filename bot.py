import os
import telebot
from telebot import types
from datetime import datetime
import pytz

# Lấy Token từ GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Cấu hình ID
SOURCE_CHANNEL_ID = -1003740753455  # ID kênh nguồn của bạn
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Biến tạm để lưu ID tin nhắn mới nhất (Sẽ reset khi restart bot trên GitHub)
# Để tối ưu hơn, bạn nên đăng 1 bài mới vào kênh ngay sau khi bot online
latest_msg_id = None

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

# Lắng nghe tin nhắn mới từ kênh nguồn để cập nhật ID bài viết
@bot.channel_post_handler(func=lambda message: message.chat.id == SOURCE_CHANNEL_ID)
def update_latest_link(message):
    global latest_msg_id
    latest_msg_id = message.message_id
    print(f"Đã cập nhật bài mới nhất: {latest_msg_id}")

@bot.callback_query_handler(func=lambda call: call.data == "get_link_today")
def handle_get_link(call):
    global latest_msg_id
    
    # Lấy thời gian thực tại Việt Nam
    now_vn = datetime.now(VN_TZ)
    ngay_hien_tai = now_vn.strftime("%d-%m-%Y")
    gio_hien_tai = now_vn.strftime("%H:%M:%S")

    if latest_msg_id:
        try:
            # Gửi thông báo trạng thái trước
            status_text = (
                f"✅ **ĐÃ TRÍCH XUẤT DỮ LIỆU NGÀY {ngay_hien_tai}**\n"
                f"⏰ Thời gian: {gio_hien_tai}\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            bot.send_message(call.message.chat.id, status_text, parse_mode='Markdown')
            
            # Copy bài viết mới nhất từ kênh sang cho khách
            bot.copy_message(
                chat_id=call.message.chat.id,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_id=latest_msg_id
            )
            
            # Gửi thêm nút hỗ trợ bên dưới
            sub_markup = types.InlineKeyboardMarkup()
            sub_markup.add(types.InlineKeyboardButton(text="👤 HỖ TRỢ BÁO LỖI LINK", url="https://t.me/Beshanday"))
            bot.send_message(call.message.chat.id, "Chúc bạn xem vui vẻ! Nếu link lỗi hãy báo Admin.", reply_markup=sub_markup)
            
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Lỗi: Bot chưa có quyền Admin trong kênh nguồn.")
    else:
        # Nếu bot vừa khởi động và chưa thấy bài mới nào
        bot.send_message(call.message.chat.id, "⚠️ Hiện tại chưa có bài mới. Vui lòng đợi Admin đăng bài vào kênh nhé!")

bot.infinity_polling()
