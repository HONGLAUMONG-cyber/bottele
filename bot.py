import os
import telebot
import uuid
import time
from datetime import datetime, timedelta
import pytz
from telebot import types

# 1. CẤU HÌNH
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot" # Đảm bảo đúng username bot của bạn

link_storage = {}
LATEST_BATCH_ID = None 

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

# --- SỬA LỆNH /xemngay TẠI ĐÂY ---
@bot.message_handler(commands=['xemngay'])
def handle_xem_ngay(message):
    global LATEST_BATCH_ID
    user_name = message.from_user.first_name
    
    if LATEST_BATCH_ID and LATEST_BATCH_ID in link_storage:
        share_link = f"https://t.me/{BOT_USERNAME}?start={LATEST_BATCH_ID}"
        
        # Giao diện tin nhắn theo mẫu bạn gửi
        welcome_text = (
            f"Chào mừng ✪ {user_name} ✪ đến với **Hồng Lâu Mộng** 😊\n"
            f"❄️ Vui lòng Đừng Chặn BOT để nhận link mới nha! ❄️"
        )
        
        # Tạo nút bấm Inline
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", url=share_link)
        markup.add(btn_link)
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "ℹ️ Hiện chưa có link nào được tạo. Sếp vui lòng bấm /start để tạo link mới nhé!")

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            try:
                bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                time.sleep(1)
                now_vn = get_vn_time()
                
                # Tin nhắn kết thúc khi khách nhận xong bài
                finish_text = (
                    f"✅ **ĐÃ GỬI XONG ALBUM NGÀY**\n"
                    f"📅 `{now_vn.strftime('%d-%m-%Y')}` | ⏰ `{now_vn.strftime('%H:%M:%S')}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💈 Đã gửi xong link Tổng: {len(msg_ids)} bài (30p qua)\n"
                    f"📊 Tình trạng lượt dùng: 0/5 lượt.\n"
                    f"📺 *Lưu ý: Đợi 30 phút để hệ thống reset nhé!*"
                )

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Xem Thêm Link Ngày Khác 🎭", url="https://t.me/Tramgiaitri"))
                markup.add(types.InlineKeyboardButton(text="Hỗ Trợ Admin 👤", url="https://t.me/Beshanday"))
                
                bot.send_message(message.chat.id, finish_text, reply_markup=markup, parse_mode='Markdown')
            except:
                bot.send_message(message.chat.id, "❌ Lỗi: Bài viết không tồn tại.")
    else:
        # Khi nhấn /start bình thường
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK 30 PHÚT QUA", callback_data="gen_link"))
        bot.send_message(message.chat.id, f"Chào mừng {message.from_user.first_name}! Bấm nút để tạo link.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_link")
def handle_gen_link(call):
    global LATEST_BATCH_ID
    user_id = call.message.chat.id
    try:
        tmp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = tmp_msg.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        valid_ids = []
        now = datetime.now(pytz.utc)
        thirty_mins_ago = now - timedelta(minutes=30)

        for m_id in range(max_id - 1, max_id - 30, -1):
            try:
                check_msg = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, m_id)
                msg_date = datetime.fromtimestamp(check_msg.forward_date, pytz.utc)
                bot.delete_message(STORAGE_GROUP_ID, check_msg.message_id)

                if msg_date >= thirty_mins_ago:
                    valid_ids.append(m_id)
                else:
                    break
            except: continue

        if not valid_ids:
            bot.send_message(user_id, "ℹ️ Không có bài mới trong 30 phút qua.")
            return

        valid_ids.sort()
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=valid_ids)
        except: pass

        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = valid_ids
        LATEST_BATCH_ID = batch_id 
        
        bot.send_message(user_id, "✅ **Đã tạo xong link bài mới nhất!**\n\nSếp có thể gõ /xemngay để kiểm tra giao diện nút bấm.", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(user_id, f"❌ Lỗi: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
