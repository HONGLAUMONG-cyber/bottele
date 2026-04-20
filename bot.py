import os
import telebot
import uuid
import time
from datetime import datetime
import pytz  # Cần cài đặt: pip install pytz
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot"

link_storage = {}

# Hàm lấy thời gian Việt Nam
def get_vn_time_str():
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz_vn)
    return now.strftime("%d-%m-%Y"), now.strftime("%H:%M:%S")

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            try:
                # 1. Nhả toàn bộ bài sạch ra cho khách
                bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                
                # Nghỉ 1 giây để bảng tin nhắn hiện sau cùng
                time.sleep(1)

                # 2. Lấy thời gian hiện tại
                ngay, gio = get_vn_time_str()

                # 3. Nội dung tin nhắn kết thúc (Mẫu bạn yêu cầu)
                finish_text = (
                    f"✅ **ĐÃ GỬI XONG ALBUM NGÀY**\n"
                    f"📅 `{ngay}` | ⏰ `{gio}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💈 Đã gửi xong link Tổng: 5/5 (Link)\n"
                    f"📊 Tình trạng lượt dùng:\n"
                    f"Còn lại: 0/5 lượt nhận link nhanh.\n"
                    f"📺 *Lưu ý: Nếu dùng hết 5 lượt, sếp vui lòng đợi 30 phút để hệ thống reset lại nhé!*"
                )

                # 4. Tạo 2 nút bấm
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Kênh Giải Trí 🎭", url="https://t.me/Tramgiaitri"))
                markup.add(types.InlineKeyboardButton(text="Hỗ Trợ Admin 👤", url="https://t.me/Beshanday"))
                
                bot.send_message(message.chat.id, finish_text, reply_markup=markup, parse_mode='Markdown')
                
            except Exception as e:
                bot.send_message(message.chat.id, "❌ Lỗi khi gửi bài.")
        else:
            bot.send_message(message.chat.id, "❌ Link này đã hết hạn.")
    else:
        # Giao diện chào mừng khi bấm /start lần đầu
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK ALBUM MỚI", callback_data="gen_link"))
        bot.send_message(message.chat.id, "Chào mừng sếp! Bấm nút để lấy link bài mới nhất.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)
        message_ids = list(range(max_id - 50, max_id))

        # Sao lưu bài vào nhóm lưu trữ
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except: pass

        # Tạo mã link ngẫu nhiên
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = message_ids
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        
        bot.send_message(user_id, f"✅ **Đã tạo link thành công!**\n\n🔗 Link của bạn:\n`{share_link}`", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(user_id, "❌ Bot chưa được cấp quyền Admin ở kênh nguồn.")

# Dòng quan trọng nhất để chạy trên GitHub
if __name__ == "__main__":
    bot.infinity_polling()
