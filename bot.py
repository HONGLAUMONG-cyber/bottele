import os
import telebot
import uuid
import time
from telebot import types

# 1. CẤU HÌNH BIẾN HỆ THỐNG
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ID Kênh nguồn và Nhóm lưu trữ của bạn
SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot" # Hãy đảm bảo tên này đúng với bot của bạn

# Bộ nhớ tạm để lưu mã link (Sẽ mất khi bot restart)
link_storage = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    
    # TRƯỜNG HỢP 1: Khách bấm vào link deep-link (ví dụ: ?start=batch_abcd)
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            
            try:
                # Nhả toàn bộ bài/album sạch ra cho khách
                bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                
                # Nghỉ 1 giây để bảng nút hiện ra cuối cùng
                time.sleep(1)

                # HIỆN 2 NÚT BẤM KẾT THÚC
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton(text="Kênh Giải Trí 🎭", url="https://t.me/Tramgiaitri")
                btn2 = types.InlineKeyboardButton(text="Hỗ Trợ Admin 👤", url="https://t.me/Beshanday")
                markup.add(btn1)
                markup.add(btn2)
                
                bot.send_message(
                    message.chat.id, 
                    "━━━━━━━━━━━━━━━━━━━━\n✨ **Đã gửi toàn bộ nội dung!**\n❄️ Chúc bạn xem vui vẻ.", 
                    reply_markup=markup, 
                    parse_mode='Markdown'
                )
            except Exception as e:
                bot.send_message(message.chat.id, "❌ Có lỗi xảy ra khi lấy bài. Vui lòng thử lại sau.")
        else:
            bot.send_message(message.chat.id, "❌ Link này đã hết hạn hoặc không tồn tại.")
            
    # TRƯỜNG HỢP 2: Khách vào bot bình thường (Bấm /start)
    else:
        user_name = message.from_user.first_name
        welcome_text = (
            f"Chào mừng ✪ {user_name} ✪ đến với **DongBanTo** 😊\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ Bấm nút dưới đây để tạo link lấy bài mới nhất."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK ALBUM MỚI", callback_data="gen_link"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "gen_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        # Dò ID bài mới nhất từ kênh nguồn
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)
        
        # Lấy dải 50 tin nhắn gần nhất
        message_ids = list(range(max_id - 50, max_id))

        # 1. Tự động sao lưu vào nhóm lưu trữ
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except:
            pass # Bỏ qua nếu lỗi quyền admin ở nhóm

        # 2. Tạo mã Batch ID ngẫu nhiên cho link
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = message_ids

        # 3. Gửi Link cho bạn
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        
        bot.send_message(
            user_id, 
            f"✅ **ĐÃ TẠO LINK THÀNH CÔNG**\n\n🔗 Link của bạn:\n`{share_link}`", 
            parse_mode='Markdown'
        )

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có quyền Admin ở Kênh nguồn hoặc dải ID trống.")

# KHỞI CHẠY BOT - ĐẢM BẢO VIẾT ĐÚNG CÚ PHÁP
if __name__ == "__main__":
    bot.infinity_polling()
