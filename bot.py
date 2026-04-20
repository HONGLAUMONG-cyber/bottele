import os
import telebot
import uuid
import time
import json
from datetime import datetime, timedelta
import pytz
from telebot import types

# 1. CẤU HÌNH
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
CHECK_CHANNEL_ID = -1003728214800     
BOT_USERNAME = "Honglaumongg_bot"

# --- QUAN TRỌNG: Sếp hãy kiểm tra kỹ dãy số ID này ---
# Nếu ID cá nhân sếp là số dương, hãy bỏ dấu "-" đi.
ADMIN_IDS = [-8078171493, -6947506249, -7624762615, 8078171493, 6947506249, 7624762615] 

DB_FILE = "bot_data.json"
IMAGE_URL = "https://i.ibb.co/4wL5HbWk/IMG-1120.jpg"

def save_data(storage, latest_id):
    with open(DB_FILE, "w") as f:
        json.dump({"storage": storage, "latest_id": latest_id}, f)

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                return data.get("storage", {}), data.get("latest_id")
        except: return {}, None
    return {}, None

link_storage, LATEST_BATCH_ID = load_data()

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def is_subscribed(user_id):
    if user_id in ADMIN_IDS: return True
    try:
        status = bot.get_chat_member(CHECK_CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['xemngay'])
def handle_xem_ngay(message):
    global LATEST_BATCH_ID, link_storage
    if not is_subscribed(message.from_user.id):
        handle_start(message)
        return
    if LATEST_BATCH_ID and LATEST_BATCH_ID in link_storage:
        share_link = f"https://t.me/{BOT_USERNAME}?start={LATEST_BATCH_ID}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", url=share_link))
        bot.send_message(message.chat.id, f"Chào mừng ✪ {message.from_user.first_name} ✪\n❄️ Đừng chặn BOT để nhận link mới!", reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "ℹ️ Hiện chưa có link mới. Admin vui lòng tạo link trước.")

@bot.message_handler(commands=['start'])
def handle_start(message):
    global link_storage
    args = message.text.split()
    user_id = message.from_user.id

    if len(args) > 1:
        if not is_subscribed(user_id):
            bot.send_message(message.chat.id, "⚠️ Vui lòng vào kênh chính để mở khóa video!")
        else:
            batch_id = args[1]
            if batch_id in link_storage:
                try:
                    bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=link_storage[batch_id])
                    time.sleep(1)
                    now_vn = get_vn_time()
                    finish_text = (
                    f"✅ **ĐÃ GỬI XONG ALBUM NGÀY**\n"
                    f"📅 `{now_vn.strftime('%d-%m-%Y')}` | ⏰ `{now_vn.strftime('%H:%M:%S')}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💈 Đã gửi xong link Tổng: {len(link_storage[batch_id])} bài (30p qua)\n"
                    f"📊 Tình trạng lượt dùng: 0/5 lượt.\n"
                    f"📺 *Lưu ý: Đợi 30 phút để hệ thống reset nhé!*"
                )

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Xem Thêm Link Ngày Khác 🎭", url="https://t.me/Tramgiaitri"))
                markup.add(types.InlineKeyboardButton(text="Hỗ Trợ Admin 👤", url="https://t.me/Beshanday"))
                
                bot.send_message(message.chat.id, finish_text, reply_markup=markup, parse_mode='Markdown')
                return
                except: pass
        return

    # GIAO DIỆN KHÓA VIDEO
    lock_text = f"👤 {message.from_user.first_name} 🆔 `{user_id}`\n**TÀI KHOẢN ĐANG BỊ KHÓA**‼️\n\nTham gia kênh để mở khóa:\nhttps://t.me/HomeHonglaumong"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🚀 THAM GIA NGAY", url="https://t.me/HomeHonglaumong"))
    
    if is_subscribed(user_id):
        markup.add(types.InlineKeyboardButton(text="🚀 XEM NGÀY HÔM NAY", callback_data="guest_xemngay"))
    if user_id in ADMIN_IDS:
        markup.add(types.InlineKeyboardButton(text="🛠 QUẢN TRỊ: TẠO LINK 30P", callback_data="gen_link"))

    bot.send_photo(message.chat.id, photo=IMAGE_URL, caption=lock_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global LATEST_BATCH_ID, link_storage
    user_id = call.from_user.id

    if call.data == "gen_link":
        # SỬA LỖI KIỂM TRA ADMIN
        if user_id not in ADMIN_IDS:
            bot.send_message(user_id, f"⚠️ Sếp không có quyền! ID của sếp là: `{user_id}`\n(Hãy copy số này dán vào danh sách ADMIN_IDS trong code)")
            bot.answer_callback_query(call.id)
            return
            
        try:
            bot.answer_callback_query(call.id, "Đang quét bài 30p qua...")
            tmp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
            max_id = tmp_msg.message_id
            bot.delete_message(SOURCE_CHANNEL_ID, max_id)
            
            valid_ids = []
            now = datetime.now(pytz.utc)
            thirty_mins_ago = now - timedelta(minutes=30)
            
            for m_id in range(max_id - 1, max_id - 50, -1):
                try:
                    check_msg = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, m_id)
                    msg_date = datetime.fromtimestamp(check_msg.forward_date, pytz.utc)
                    bot.delete_message(STORAGE_GROUP_ID, check_msg.message_id)
                    if msg_date >= thirty_mins_ago: valid_ids.append(m_id)
                    else: break
                except: continue

            if not valid_ids:
                bot.send_message(user_id, "ℹ️ Không tìm thấy bài nào đăng trong 30 phút qua.")
                return

            valid_ids.sort()
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=valid_ids)
            
            batch_id = f"batch_{uuid.uuid4().hex[:8]}"
            link_storage[batch_id] = valid_ids
            LATEST_BATCH_ID = batch_id 
            save_data(link_storage, LATEST_BATCH_ID)
            
            bot.send_message(user_id, "✅ **TẠO LINK THÀNH CÔNG!**\nKhách đã có thể dùng /xemngay.")
        except Exception as e:
            bot.send_message(user_id, f"❌ Lỗi hệ thống: {e}")

    elif call.data == "guest_xemngay":
        handle_xem_ngay(call.message)

if __name__ == "__main__":
    bot.infinity_polling()
