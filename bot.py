import os
import telebot
import uuid
import time
import json
from datetime import datetime, timedelta
import pytz
from telebot import types

# --- 1. CẤU HÌNH ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
CHECK_CHANNEL_ID = -1003728214800     
BOT_USERNAME = "Honglaumongg_bot"

# Danh sách Admin
ADMIN_IDS = [-8078171493, -6947506249, -7624762615, 8078171493, 6947506249, 7624762615] 

DB_FILE = "bot_data.json"
USER_FILE = "user_list.json" 
IMAGE_URL = "https://i.ibb.co/4wL5HbWk/IMG-1120.jpg"

# --- 2. HÀM LƯU TRỮ ---
def save_data(storage, latest_id):
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump({"storage": storage, "latest_id": latest_id}, f, ensure_ascii=False)
    except: pass

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data.get("storage", {}), data.get("latest_id")
        except: return {}, None
    return {}, None

def add_user(user_id):
    users = []
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                users = json.load(f)
        except: users = []
    if user_id not in users:
        users.append(user_id)
        with open(USER_FILE, "w") as f:
            json.dump(users, f)

def get_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

link_storage, LATEST_BATCH_ID = load_data()

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def is_subscribed(user_id):
    if user_id in ADMIN_IDS: return True
    try:
        status = bot.get_chat_member(CHECK_CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- 3. LỆNH THÔNG BÁO ---
@bot.message_handler(commands=['thongbao'])
def handle_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ Quyền hạn này chỉ dành cho Admin!")
        return
    users = get_users()
    if not users:
        bot.reply_to(message, "ℹ️ Chưa có khách nào trong danh sách.")
        return
    bot.send_message(message.chat.id, f"🚀 Đang gửi thông báo tới {len(users)} người...")
    count, blocked = 0, 0
    for uid in users:
        try:
            if message.reply_to_message:
                bot.copy_message(uid, message.chat.id, message.reply_to_message.message_id)
            else:
                text = message.text.replace('/thongbao', '').strip()
                if not text: return
                bot.send_message(uid, text)
            count += 1
            time.sleep(0.05)
        except: blocked += 1
    bot.send_message(message.chat.id, f"✅ Xong! Thành công: {count}, Thất bại: {blocked}")

# --- 4. LỆNH START ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    global link_storage, LATEST_BATCH_ID
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    add_user(user_id)
    args = message.text.split()

    if len(args) > 1:
        if not is_subscribed(user_id):
            bot.send_message(message.chat.id, "⚠️ **LỖI:** Sếp phải tham gia kênh chính mới xem được video này!")
        else:
            batch_id = args[1]
            if batch_id in link_storage:
                msg_ids = link_storage[batch_id]
                try:
                    bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                    now_vn = get_vn_time()
                    finish_text = (
                        f"✅ **ĐÃ GỬI XONG ALBUM NGÀY**\n"
                        f"📅 `{now_vn.strftime('%d-%m-%Y')}` | ⏰ `{now_vn.strftime('%H:%M:%S')}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 Đã gửi xong link Tổng: {len(msg_ids)} bài\n"
                        f"📺 *Lưu ý: Hệ thống tự reset sau 30 phút!*"
                    )
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text="📅 XEM TIẾP NGÀY KHÁC", url="https://t.me/Tramgiaitri"))
                    markup.add(types.InlineKeyboardButton(text="👤 HỖ TRỢ ADMIN", url="https://t.me/Beshanday"))
                    bot.send_message(message.chat.id, finish_text, reply_markup=markup, parse_mode='Markdown')
                    return
                except: pass
        return

    # Giao diện khóa video ĐẦY ĐỦ THÔNG SỐ
    lock_text = (
        f"Thông tin tài khoản của bạn :\n"
        f"👤 {user_name} 🆔 `{user_id}`\n"
        f"**ĐANG BỊ KHÓA XEM VIDEO**‼️\n\n"
        f"✅ Cách mở khóa nhóm : HÃY THAM GIA KÊNH CHÍNH ĐỂ MỞ KHOÁ\n\n"
        f"🔗Liên kết để tham gia :\n"
        f"https://t.me/HomeHonglaumong\n\n"
        f"🔐 Video đã bị khóa : 374.968\n"
        f"🔐 Ảnh đã bị khóa : 512.097\n"
        f"🔐 Tệp đã bị khóa : 179.225"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🚀 THAM GIA NGAY", url="https://t.me/HomeHonglaumong"))
    if is_subscribed(user_id):
        markup.add(types.InlineKeyboardButton(text="🚀 XEM NGÀY HÔM NAY", callback_data="guest_xemngay"))
    if user_id in ADMIN_IDS:
        markup.add(types.InlineKeyboardButton(text="🛠 QUẢN TRỊ: TẠO LINK 30P", callback_data="gen_link"))
    bot.send_photo(message.chat.id, photo=IMAGE_URL, caption=lock_text, reply_markup=markup, parse_mode='Markdown')

# --- 5. LỆNH XEMNGAY ---
@bot.message_handler(commands=['xemngay'])
def handle_xem_ngay(message):
    global LATEST_BATCH_ID, link_storage
    if not is_subscribed(message.from_user.id):
        return handle_start(message)
    if LATEST_BATCH_ID and LATEST_BATCH_ID in link_storage:
        share_link = f"https://t.me/{BOT_USERNAME}?start={LATEST_BATCH_ID}"
        welcome_text = (
            f"Chào mừng ✪ {message.from_user.first_name} ✪ đến với **Hồng Lâu Mộng** 😊\n"
            f"❄️ Vui lòng Đừng Chặn BOT để nhận link mới nha! ❄️"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LINK HÔM NAY - Ấn vào đây", url=share_link))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "ℹ️ Hiện chưa có link mới. Admin vui lòng tạo link trước.")

# --- 6. XỬ LÝ NÚT BẤM ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global LATEST_BATCH_ID, link_storage
    user_id = call.from_user.id
    if call.data == "gen_link":
        if user_id not in ADMIN_IDS: return
        try:
            bot.answer_callback_query(call.id, "Đang quét bài...")
            tmp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
            max_id = tmp_msg.message_id
            bot.delete_message(SOURCE_CHANNEL_ID, max_id)
            valid_ids = []
            now = datetime.now(pytz.utc)
            thirty_mins_ago = now - timedelta(minutes=30)
            for m_id in range(max_id - 1, max_id - 60, -1):
                try:
                    check_msg = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, m_id)
                    msg_date = datetime.fromtimestamp(check_msg.forward_date, pytz.utc)
                    bot.delete_message(STORAGE_GROUP_ID, check_msg.message_id)
                    if msg_date >= thirty_mins_ago: valid_ids.append(m_id)
                    else: break
                except: continue
            if not valid_ids:
                bot.send_message(user_id, "ℹ️ 30p qua không có bài mới.")
                return
            valid_ids.sort()
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=valid_ids)
            new_id = f"batch_{uuid.uuid4().hex[:8]}"
            link_storage[new_id] = valid_ids
            LATEST_BATCH_ID = new_id 
            save_data(link_storage, LATEST_BATCH_ID)
            bot.send_message(user_id, f"✅ Thành công! Link: `https://t.me/{BOT_USERNAME}?start={new_id}`")
        except Exception as e:
            bot.send_message(user_id, f"❌ Lỗi: {e}")
    elif call.data == "guest_xemngay":
        handle_xem_ngay(call.message)

if __name__ == "__main__":
    bot.infinity_polling()
