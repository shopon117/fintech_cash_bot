# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3

# ১. বটের কনফিগারেশন এবং টোকেন সেটআপ (আপনার আসল টোকেন ও আইডি এখানে বসানো আছে)
BOT_TOKEN = "8924250554:AAFRKaBOlxkgcUtWBAiT2DOMs7k1mEF6Cm0"
ADMIN_ID = 5547760831  # আপনার অ্যাডমিন আইডি

UPDATE_CHANNEL = "@new_update100"
PROOF_CHANNEL = "@new_proof100"

bot = telebot.TeleBot(BOT_TOKEN)

# ২. ডেটাবেজ সেটআপ (সাইন-আপ বোনাস ১০০০ টাকা ডিফল্ট)
def init_db():
    conn = sqlite3.connect('fintech_wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance REAL DEFAULT 1000.0,
            status TEXT DEFAULT 'inactive',
            referred_by INTEGER DEFAULT NULL,
            ref_bonus_credited INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# channel জয়েন চেক করার ফাংশন
def check_joined(user_id):
    try:
        member1 = bot.get_chat_member(UPDATE_CHANNEL, user_id)
        member2 = bot.get_chat_member(PROOF_CHANNEL, user_id)
        
        valid_statuses = ['member', 'administrator', 'creator']
        if member1.status in valid_statuses and member2.status in valid_statuses:
            return True
        return False
    except Exception:
        return False

# বাধ্যতামূলক জয়েনিং কীবোর্ড
def join_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📢 আপডেট চ্যানেল", url="https://t.me/new_update100")
    btn2 = types.InlineKeyboardButton("🧾 পেমেন্ট প্রুফ চ্যানেল", url="https://t.me/new_proof100")
    btn3 = types.InlineKeyboardButton("🟢 জয়েন করেছি (Joined)", callback_data="check_channels")
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    return markup

# প্রধান মেনু কীবোর্ড (কোনো ইমোজি নেই, ১০০% ফিক্সড টেক্সট)
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('আমার প্রোফাইল')
    btn2 = types.KeyboardButton('রেফার করুন')
    btn3 = types.KeyboardButton('উইথড্র')
    btn4 = types.KeyboardButton('অ্যাক্টিভ')
    btn5 = types.KeyboardButton('সাপোর্ট')
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)
    return markup

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    referred_by = None
    if len(message.text.split()) > 1:
        try:
            referred_by = int(message.text.split()[1])
            if referred_by == user_id:
                referred_by = None
        except ValueError:
            referred_by = None

    conn = sqlite3.connect('fintech_wallet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, balance, referred_by) VALUES (?, ?, ?, 1000.0, ?)",
            (user_id, username, first_name, referred_by)
        )
        conn.commit()
    conn.close()

    welcome_text = (
        "Welcome to Fintech Cash Wallet!\n\n"
        "সবচেয়ে বিশ্বস্ত ডিজিটাল আর্নিং ও অনলাইন ওয়ালেট প্ল্যাটফর্মে আপনাকে স্বাগতম!\n\n"
        "ধামাকা অফার: আমাদের বটে নতুন অ্যাকাউন্ট খোলায় আপনি পেয়ে গেছেন ১০০০ টাকা সাইন-আপ বোনাস! যা আপনার প্রোফাইলে যোগ করে দেওয়া হয়েছে।\n\n"
        "Fintech Cash Wallet হলো একটি আধুনিক ও নিরাপদ মাধ্যম, যেখানে আপনি খুব সহজেই ঘরে বসে বন্ধুদের রেফার করার মাধ্যমে প্রতিদিন নিশ্চিত আয় করতে পারবেন।\n\n"
        "কাজ শুরু করার পূর্বে আমাদের অফিসিয়াল দুটি চ্যানেলে জয়েন করা বাধ্যতামূলক!\n"
        "নিচের চ্যানেলগুলোতে জয়েন করে 'জয়েন করেছি' বাটনে ক্লিক করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=join_keyboard())

# ইনলাইন বাটন (চ্যানেল ভেরিфикации) হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def callback_check_channels(call):
    user_id = call.from_user.id
    if check_joined(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id, 
            "অনভিন্দন! আপনি সফলভাবে আমাদের চ্যানেলে যুক্ত হয়েছেন। এখন আপনি বটের সকল ফিচার ব্যবহার করতে পারবেন।", 
            reply_markup=main_menu()
        )
    else:
        bot.answer_callback_query(call.id, "আপনি এখনো দুটি চ্যানেলে জয়েন করেননি! দয়া করে দুটি চ্যানেলেই জয়েন করুন।", show_alert=True)

# ৩. অ্যাডমিন প্যানেল কমান্ড
@bot.message_handler(commands=['active_user'])
def admin_activate_user(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        target_user_id = int(message.text.split()[1])
        
        conn = sqlite3.connect('fintech_wallet.db')
        cursor = conn.cursor()

        cursor.execute("SELECT status, referred_by, ref_bonus_credited FROM users WHERE user_id = ?", (target_user_id,))
        user_info = cursor.fetchone()

        if not user_info:
            bot.reply_to(message, f"ইউজার আইডি {target_user_id} ডাটাবেজে পাওয়া যায়নি!")
            conn.close()
            return

        if user_info[0] == 'active':
            bot.reply_to(message, f"ইউজার {target_user_id} এর অ্যাকাউন্ট ইতিমধ্যেই অ্যাক্টিভ করা আছে।")
            conn.close()
            return

        cursor.execute("UPDATE users SET status = 'active' WHERE user_id = ?", (target_user_id,))
        
        referred_by = user_info[1]
        ref_bonus_credited = user_info[2]
        
        if referred_by and ref_bonus_credited == 0:
            cursor.execute("UPDATE users SET balance = balance + 40 WHERE user_id = ?", (referred_by,))
            cursor.execute("UPDATE users SET ref_bonus_credited = 1 WHERE user_id = ?", (target_user_id,))
            
            try:
                bot.send_message(referred_by, f"অনভিন্দন! আপনার আমন্ত্রিত ইউজার (ID: {target_user_id}) অ্যাকাউন্ট অ্যাক্টিভ করায় আপনার ব্যালেন্সে ৪০ টাকা রেফার বোনাস যোগ হয়েছে!")
            except Exception:
                pass
                
            cursor.execute("SELECT referred_by FROM users WHERE user_id = ?", (referred_by,))
            level2_data = cursor.fetchone()
            if level2_data and level2_data[0]:
                level2_referrer = level2_data[0]
                cursor.execute("UPDATE users SET balance = balance + 20 WHERE user_id = ?", (level2_referrer,))
                try:
                    bot.send_message(level2_referrer, f"অনভিন্দন! আপনার লেভেল-২ রেফারেল ইউজার অ্যাকাউন্ট অ্যাক্টিভ করায় আপনার ব্যালেন্সে ২০ টাকা বোনাস যোগ হয়েছে!")
                except Exception:
                    pass
                    
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"ইউজার {target_user_id} এর অ্যাকাউন্ট সফলভাবে অ্যাক্টিভ করা হয়েছে।")
        
        try:
            bot.send_message(target_user_id, "অনভিন্দন! অ্যাডমিন আপনার পেমেন্ট ভেরিফাই করে আপনার অ্যাকাউন্টটি সম্পূর্ণ অ্যাক্টিভ করে দিয়েছেন। এখন আপনার রেফারেল লিংক এবং উইথড্র সিস্টেম কাজ করবে।")
        except Exception:
            pass
            
    except IndexError:
        bot.reply_to(message, "ভুল ফরম্যাট! সঠিক নিয়ম: /active_user USER_ID")
    except ValueError:
        bot.reply_to(message, "ভুল ইউজার আইডি! আইডিটি শুধুমাত্র সংখ্যায় হতে হবে।")
    except Exception as e:
        bot.reply_to(message, f"একটি ত্রুটি ঘটেছে: {str(e)}")

# ৪. টেক্সট মেসেজ এবং বাটন লজিক হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user_text = message.text

    if not check_joined(user_id):
        bot.send_message(
            message.chat.id, 
            "দুঃখিত! বটের বাটনগুলো ব্যবহার করতে হলে আপনাকে অবশ্যই আমাদের দুটি চ্যানেলে জয়েন থাকতে হবে।", 
            reply_markup=join_keyboard()
        )
        return

    # ১. আমার প্রোফাইল বাটন লজিক
    if user_text == 'আমার প্রোফাইল':
        conn = sqlite3.connect('fintech_wallet.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance, status FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ? AND status = 'active'", (user_id,))
        active_refers = cursor.fetchone()[0]
        conn.close()
        
        current_balance = user_data[0] if user_data else 1000.0
        account_status = user_data[1] if user_data else 'inactive'
        
        status_text = "অ্যাক্টিভ (Active)" if account_status == 'active' else "ইন-অ্যাক্টিভ (In-active)"
        profile_text = (
            "আপনার Fintech Cash Wallet প্রোফাইল ড্যাশবোর্ড\n\n"
            f"নাম: {message.from_user.first_name}\n"
            f"ইউজার আইডি: {message.from_user.id}\n"
            f"আপনার মোট ব্যালেন্স: {current_balance:.2f} টাকা (১০০০ টাকা বোনাসসহ)\n"
            f"একটিভ রেফারেল: {active_refers} জন\n"
            f"অ্যাকাউন্ট স্ট্যাটাস: {status_text}\n\n"
            "নোট: অ্যাকাউন্ট ইন-অ্যাক্টিভ থাকলে রেফারেল কমিশন ব্যালেন্সে যোগ হবে না এবং উইথড্র করা যাবে না"
        )
        bot.send_message(message.chat.id, profile_text)

    # ২. রেফার করুন বাটন লজিক (১০০% ক্র্যাশ-প্রুফ ফিক্সড সেকশন)
    elif user_text == 'রেফার করুন':
        conn = sqlite3.connect('fintech_wallet.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ? AND status = 'active'", (user_id,))
        total_refers = cursor.fetchone()[0]
        conn.close()

        refer_link = f"https://t.me/ss_fintech_cash_bot?start={user_id}"
        refer_text = (
            "Fintech Cash Wallet রেফারেল প্রোগ্রাম\n\n"
            f"আপনার মোট একটিভ রেফারেল: {total_refers} জন\n\n"
            f"আপনার ইউনিক রেফারেল লিংক:\n{refer_link}\n\n"
            "রেফারেল কমিশন সিস্টেম:\n"
            "লেভেল ১ (সরাসরি রেফার) -> ৪০ টাকা বোনাস!\n"
            "লেভেল ২ (বন্ধুর বন্ধু রেফার) -> ২০ টাকা বোনাস!\n\n"
            "গুরুত্বপূর্ণ নিয়ম: আপনি যাকে রেফার করবেন, সে ১০০ টাকা দিয়ে তার অ্যাকাউন্ট অ্যাক্টিভ করলেই কেবল আপনার ব্যালেন্সে রেফারের টাকা যোগ হবে। সে অ্যাক্টিভ না করা পর্যন্ত কোনো বোনাস পাবেন না।"
        )
        bot.send_message(message.chat.id, refer_text, disable_web_page_preview=True)

    # ৩. উইথড্র বাটন লজিক
    elif user_text == 'উইথড্র':
        conn = sqlite3.connect('fintech_wallet.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance, status FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ? AND status = 'active'", (user_id,))
        active_refers = cursor.fetchone()[0]
        conn.close()
        
        current_balance = user_data[0] if user_data else 1000.0
        account_status = user_data[1] if user_data else 'inactive'

        if account_status != 'active':
            withdraw_lock_text = (
                "উইথড্র ব্লক করা হয়েছে!\n\n"
                "দুঃখিত, আপনার অ্যাকাউন্টটি এখনো ইন-অ্যাক্টিভ (In-active)।\n"
                "Fintech Cash Wallet-এর নিয়ম অনুযায়ী, অ্যাকাউন্ট ১০০ টাকা দিয়ে অ্যাক্টিভ না করা পর্যন্ত টাকা উত্তোলন করা সম্পূর্ণ নিষিদ্ধ।"
            )
            bot.send_message(message.chat.id, withdraw_lock_text)
            return

        if active_refers < 20:
            withdrawable_balance = current_balance - 1000.0
            
            if withdrawable_balance < 100:
                withdraw_text = (
                    "Fintech Cash Wallet উইথড্রাল সিস্টেম\n\n"
                    f"💵 আপনার মোট ব্যালেন্স: {current_balance:.2f} টাকা\n"
                    f"🔒 লকড বোনাস ব্যালেন্স: 1000.00 টাকা (২০টি একটিভ রেফার হলে আনলক হবে)\n"
                    f"💵 আপনার উত্তোলনযোগ্য রেফারের ব্যালেন্স: {withdrawable_balance:.2f} টাকা\n"
                    "সর্বনিম্ন উইথড্র পরিমাণ: ১০০ টাকা\n\n"
                    "নোট: আপনার সাইন-আপ বোনাসের ১০০০ টাকা তুলতে হলে আপনাকে অবশ্যই ২০টি সফল (Active) রেফার কমপ্লিট করতে হবে। তবে রেফারের টাকা ১০০ টাকা হলেই আপনি যেকোনো সময় তুলে নিতে পারবেন।"
                )
                bot.send_message(message.chat.id, withdraw_text)
            else:
                bot.send_message(
                    message.chat.id, 
                    f"উইথড্র করার জন্য আপনার বিকাশ/নগদ/রকেট নম্বর এবং অ্যামাউন্টটি আমাদের সাপোর্ট আইডিতে পাঠান।\n\n"
                    f"আপনার বর্তমান উত্তোলনযোগ্য ব্যালেন্স: {withdrawable_balance:.2f} টাকা।\n"
                    f"নোট: আপনার অ্যাকাউন্টের ১০০০ টাকা সাইন-আপ বোনাসটি লক রয়েছে, কারণ আপনার একটিভ রেফার ২০ জনের কম ({active_refers}/20)"
                )
        else:
            if current_balance < 100:
                bot.send_message(message.chat.id, f"দুঃখিত! উইথড্র করার জন্য আপনার অ্যাকাউন্টে সর্বনিম্ন ১০০ টাকা ব্যালেন্স থাকতে হবে। আপনার বর্তমান ব্যালেন্স: {current_balance:.2f} টাকা।")
            else:
                bot.send_message(
                    message.chat.id, 
                    f"অনভিন্দন! আপনার ২০টির বেশি একটিভ রেফার থাকায় আপনার সাইন-আপ বোনাসসহ সমস্ত টাকা আনলক হয়ে গেছে।\n\n"
                    f"আপনার মোট উত্তোলনযোগ্য ব্যালেন্স: {current_balance:.2f} টাকা।\n"
                    f"টাকা তোলার জন্য আপনার পেমেন্ট নম্বর ও অ্যামাউন্ট লিখে নিচের সাপোর্ট বাটনে ক্লিক করে অ্যাডমিনকে পাঠান।"
                )

    # ৪. অ্যাক্টিভ বাটন লজিক
    elif user_text == 'অ্যাক্টিভ':
        active_text = (
            "Fintech Cash Wallet অ্যাকাউন্ট অ্যাক্টিভেশন\n\n"
            "আপনার অ্যাকাউন্টটি সম্পূর্ণ ভেরিফাইড এবং লাইফটাইম অ্যাক্টিভ করতে মাত্র ১০০ টাকা ওয়ান-টাইম ফি প্রদান করতে হবে।\n\n"
            "নিচের যেকোনো একটি অ্যাকাউন্টে ১০০ টাকা Send Money করুন:\n"
            "বিকাশ (Personal): 01833084108\n"
            "নগদ (Personal): 01833084108\n"
            "রকেট (Personal): 018330841088\n\n"
            "টাকা পাঠানোর পর করণীয়:\n"
            "টাকা সফলভাবে পাঠানোর পর, পেমেন্টের Transaction ID (TrxID) এবং যে নম্বর থেকে টাকা পাঠিয়েছেন তা কপি করে নিচের সাপোর্ট বাটনে ক্লিক করে অ্যাডমিনকে সরাসরি মেসেজ দিন।"
        )
        bot.send_message(message.chat.id, active_text)

    # ৫. সাপোর্ট বাটন লজিক
    elif user_text == 'সাপোর্ট':
        support_text = (
            "Fintech Cash Wallet হেল্প ও কাস্টমার সাপোর্ট\n\n"
            "আপনার অ্যাকাউন্ট অ্যাক্টিভেশন, পেমেন্ট ভেরিфикации, উইথড্র বা অন্য যেকোনো সমস্যার দ্রুত সমাধানের জন্য নিচের বাটনে ক্লিক করে সরাসরি আমাদের অ্যাডমিন আইডিতে মেসেজ দিন:\n\n"
            "নোট: কাইন্ডলি মেসেজ দেওয়ার পর কিছুক্ষণ অপেক্ষা করুন, আমাদের টিম দ্রুত আপনার পেমেন্ট বা সমস্যা চেক করে সমাধান করে দেবে।"
        )
        
        markup_support = types.InlineKeyboardMarkup()
        btn_admin = types.InlineKeyboardButton("💬 অ্যাডমিনকে মেসেজ দিন", url="tg://user?id=5547760831")
        markup_support.add(btn_admin)
        
        bot.send_message(message.chat.id, support_text, reply_markup=markup_support)

# বট চালু করা
if __name__ == '__main__':
    print("Fintech Cash Wallet Bot is running perfectly with zero error risks...")
    bot.infinity_polling()
