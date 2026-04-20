import os
import telebot
import uuid
from telebot import types

# 1. Cấu hình
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

SOURCE_CHANNEL_ID = -1003740753455    
STORAGE_GROUP_ID = -1003842996683     
BOT_USERNAME = "Honglaumongg_bot"

link_storage = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    if len(args) > 1:
        batch_id = args[1]
        if batch_id in link_storage:
            msg_ids = link_storage[batch_id]
            bot.copy_messages(chat_id=message.chat.id, from_chat_id=SOURCE_CHANNEL_ID, message_ids=msg_ids)
        else:
            bot.send_message(message.chat.id, "❌ Link đã hết hạn.")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔗 LẤY LINK ALBUM MỚI", callback_data="gen_link"))
        bot.send_message(message.chat.id, f"Chào mừng ✪ {message.from_user.first_name} ✪\nBấm nút để lấy link bài mới.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_link")
def handle_gen_link(call):
    user_id = call.message.chat.id
    try:
        # Dò ID bài mới nhất
        check = bot.send_message(SOURCE_CHANNEL_ID, ".")
        max_id = check.message_id
        bot.delete_message(SOURCE_CHANNEL_ID, max_id)
        message_ids = list(range(max_id - 50, max_id))

        # 1. Sao lưu vào nhóm lưu trữ
        try:
            bot.copy_messages(chat_id=STORAGE_GROUP_ID, from_chat_id=SOURCE_CHANNEL_ID, message_ids=message_ids)
        except: pass

        # 2. Tạo mã link
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        link_storage[batch_id] = message_ids

        # 3. Gửi link và đoạn kết thúc
        share_link = f"https://t.me/{BOT_USERNAME}?start={batch_id}"
        bot.send_message(user_id, f"✅ **Link của bạn:**\n`{share_link}`", parse_mode='Markdown')
        
        # --- ĐOẠN KẾT THÚC ---
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="👤 Liên hệ Admin", url="https://t.me/Beshanday"))
        bot.send_message(user_id, "━━━━━━━━━━━━━━\n✨ Gửi link xong rồi nhé! Chúc bạn xem vui vẻ.", reply_markup=markup)

    except Exception as e:
        bot.send_message(user_id, "❌ Lỗi: Kiểm tra quyền Admin.")

# Dòng này BẮT BUỘC phải viết đúng như sau:
if __name__ == "__main__":
    bot.infinity_polling()
