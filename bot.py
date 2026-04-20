import os
import telebot
import uuid # Dùng để tạo mã link ngẫu nhiên
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot" # Thay đúng username bot của bạn

# Lưu trữ tạm thời link (Trong thực tế nên dùng Database)
link_storage = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    # 1. Nhả bài cho khách
            bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
            
            # 2. ĐOẠN HIỆN THÔNG BÁO TỔNG KẾT VÀ 2 NÚT BẤM (GIỐNG MẪU)
            from datetime import datetime
            today = datetime.now().strftime("%d-%m-%Y")
            
            footer_text = (
                f"✅ **ĐÃ GỬI XONG ALBUM NGÀY {today}**\n"
                f"🔥 Đã gửi xong link Tổng: **{len(msg_ids)}/{len(msg_ids)} (Link)**\n\n"
                f"📊 **Tình trạng lượt dùng:**\n"
                f"🎟 Còn lại: **5/5** lượt nhận link nhanh.\n"
                f"⌛ _Lưu ý: Nếu dùng hết 5 lượt, sếp vui lòng đợi 30 phút để hệ thống reset lại nhé!_"
            )
            
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="📅 XEM TIẾP NGÀY KHÁC", url="https://t.me/Tramgiaitri")
            btn2 = types.InlineKeyboardButton(text="👤 HỖ TRỢ BÁO LỖI LINK", url="https://t.me/Beshanday")
            markup.add(btn1)
            markup.add(btn2)
            
            bot.send_message(message.chat.id, footer_text, reply_markup=markup, parse_mode='Markdown')
    else:
        # Giao diện chào mừng bình thường
        welcome_text = f"Chào mừng ✪ {message.from_user.first_name} ✪\n✨ Bấm nút để lấy link bài mới nhất."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK ALBUM", callback_data="get_link"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        # Dò ID bài mới nhất
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)
        
        # Lấy dải 50 ID (Album/Video)
        message_ids = list(range(max_id - 10, max_id))

        # 1. Sao lưu vào nhóm lưu trữ trước
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except: pass

        # 2. Tạo mã link ngẫu nhiên
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = message_ids # Lưu danh sách ID vào bộ nhớ

        # 3. Gửi link cho người dùng
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        bot.send_message(user_id, f"✅ Đã tạo link thành công!\n\n🔗 Link của bạn:\n`{share_link}`", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Bot chưa có quyền Admin.")

if __name__ == "__main__":
    bot.infinity_polling()
