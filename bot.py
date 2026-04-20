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
BOT_USERNAME = "Honglaumongg_bot"

link_storage = {}

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            try:
                # Gửi album sạch cho khách
                bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
                
                time.sleep(1)
                now_vn = get_vn_time()
                
                # Nội dung tin nhắn kết thúc
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
                bot.send_message(message.chat.id, "❌ Lỗi: Không thể copy bài (có thể bài đã bị xóa).")
        else:
            bot.send_message(message.chat.id, "❌ Link hết hạn hoặc không tìm thấy bài trong 30p qua.")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK 30 PHÚT QUA", callback_data="gen_link"))
        bot.send_message(message.chat.id, "Chào sếp! Bấm nút để lọc bài trong 30 phút gần nhất.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        # Lấy ID tin nhắn mới nhất bằng cách gửi tin nhắn tạm
        tmp_msg = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = tmp_msg.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)

        valid_ids = []
        now = datetime.now(pytz.utc) # Telegram dùng giờ UTC
        thirty_mins_ago = now - timedelta(minutes=30)

        # Quét ngược 20 tin nhắn gần nhất để tìm tin trong vòng 30p
        # (Không quét quá nhiều để tránh bị Telegram chặn)
        for m_id in range(max_id - 1, max_id - 21, -1):
            try:
                # Dùng forward để check thời gian (sau đó xóa đi)
                check_msg = bot.forward_message(STORAGE_GROUP_ID, SOURCE_CHANNEL_ID, m_id)
                msg_date = datetime.fromtimestamp(check_msg.forward_date, pytz.utc)
                bot.delete_message(STORAGE_GROUP_ID, check_msg.message_id)

                if msg_date >= thirty_mins_ago:
                    valid_ids.append(m_id)
                else:
                    break # Nếu gặp tin cũ hơn 30p thì dừng quét
            except:
                continue

        if not valid_ids:
            bot.send_message(user_id, "ℹ️ Không có bài mới nào trong 30 phút vừa qua.")
            return

        valid_ids.sort() # Sắp xếp lại ID cho đúng thứ tự bài đăng

        # Sao lưu và tạo link
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=valid_ids)
        except: pass

        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = valid_ids
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        
        bot.send_message(user_id, f"✅ **Đã lọc xong bài 30p qua!**\n\n🔗 Link: `{share_link}`", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(user_id, f"❌ Lỗi: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
