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
BOT_USERNAME = "Honglaumongg_bot" # <-- Sửa đúng Username bot của sếp nhé

# DANH SÁCH ADMIN (Đã cập nhật theo ID sếp gửi)
ADMIN_IDS = [-8078171493, -6947506249, -7624762615] 

link_storage = {}
LATEST_BATCH_ID = None 

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

# --- LỆNH /xemngay CHO KHÁCH ---
@bot.message_handler(commands=['xemngay'])
def handle_xem_ngay(message):
    global LATEST_BATCH_ID
    user_name = message.from_user.first_name
    
    if LATEST_BATCH_ID and LATEST_BATCH_ID in link_storage:
        share_link = f"https://t.me/{BOT_USERNAME}?start={LATEST_BATCH_ID}"
        
        welcome_text = (
            f"Chào mừng ✪ {user_name} ✪ đến với **Hồng Lâu Mộng** 😊\n"
            f"❄️ Vui lòng Đừng Chặn BOT để nhận link mới nha! ❄️"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", url=share_link)
        markup.add(btn_link)
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "ℹ️ Hiện chưa có link mới. Sếp vui lòng quay lại sau nhé!")

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    # 1. Nếu là link trả bài (Deep-link)
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            try:
                bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                time.sleep(1)
                now_vn = get_vn_time()
                
                finish_text = (
                    f"✅ **ĐÃ GỬI XONG ALBUM NGÀY**\n"
                    f"📅 `{now_vn.strftime('%d-%m-%Y')}` | ⏰ `{now_vn.strftime('%H:%M:%S')}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💈 Đã gửi xong link Tổng: {len(msg_ids)} bài (30p qua)\n"
                    f"📊 Tình trạng lượt dùng: 0/5 lượt.\n"
                    f"📺 *Lưu ý: Hệ thống sẽ tự động reset sau 30 phút!*"
                )

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="📅 XEM TIẾP NGÀY KHÁC", url="https://t.me/Tramgiaitri"))
                markup.add(types.InlineKeyboardButton(text="👤 HỖ TRỢ BÁO LỖI LINK", url="https://t.me/Beshanday"))
                
                bot.send_message(message.chat.id, finish_text, reply_markup=markup, parse_mode='Markdown')
            except:
                bot.send_message(message.chat.id, "❌ Lỗi: Bài viết không tồn tại.")
        return

    # 2. Giao diện chính /start
    markup = types.InlineKeyboardMarkup()
    # Kiểm tra nếu ID người dùng nằm trong danh sách Admin
    if message.from_user.id in ADMIN_IDS:
        markup.add(types.InlineKeyboardButton(text="🛠 QUẢN TRỊ: TẠO LINK MỚI", callback_data="gen_link"))
    
    markup.add(types.InlineKeyboardButton(text="🚀 XEM NGÀY HÔM NAY", callback_data="guest_xemngay"))
    
    bot.send_message(message.chat.id, f"Chào mừng {message.from_user.first_name} sếp đã quay trở lại!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global LATEST_BATCH_ID
    
    if call.data == "gen_link":
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⚠️ Sếp không có quyền Admin!", show_alert=True)
            return

        try:
            # Dò ID bài mới nhất
            tmp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
            max_id = tmp_msg.message_id
            bot.delete_message(SOURCE_CHANNEL_ID, max_id)

            valid_ids = []
            now = datetime.now(pytz.utc)
            thirty_mins_ago = now - timedelta(minutes=30)

            # Quét tìm bài trong 30p
            for m_id in range(max_id - 1, max_id - 35, -1):
                try:
                    check_msg = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, m_id)
                    msg_date = datetime.fromtimestamp(check_msg.forward_date, pytz.utc)
                    bot.delete_message(STORAGE_GROUP_ID, check_msg.message_id)
                    if msg_date >= thirty_mins_ago:
                        valid_ids.append(m_id)
                    else: break
                except: continue

            if not valid_ids:
                bot.send_message(call.from_user.id, "ℹ️ 30p qua không có bài mới nào.")
                bot.answer_callback_query(call.id)
                return

            valid_ids.sort()
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=valid_ids)

            batch_id = f"batch_{uuid.uuid4().hex[:8]}"
            link_storage[batch_id] = valid_ids
            LATEST_BATCH_ID = batch_id 
            
            bot.send_message(call.from_user.id, f"✅ **Admin đã tạo link thành công!**\nLink đã được cập nhật vào lệnh /xemngay.")
            bot.answer_callback_query(call.id, "Đã cập nhật link!")
            
        except Exception as e:
            bot.send_message(call.from_user.id, f"❌ Lỗi: {e}")

    elif call.data == "guest_xemngay":
        handle_xem_ngay(call.message)

if __name__ == "__main__":
    bot.infinity_polling()
