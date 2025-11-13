import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

# === TOKEN & ADMIN ===
API_TOKEN = "8568223587:AAEHaVPFcfvb-T03vsY4bcaT6jYHuRai66c"
ADMIN_ID = 7823588220
ADMIN_PASSWORD = "shoh123"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# === JSON SAQLASH ===
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "uc_options": [],
        "malumot_videos": [],
        "akavideos": [],
        "admin_card": ""
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()
authorized_admins = set()

# === HOLATLAR ===
class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_card_number = State()
    waiting_for_add_uc = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()

class OrderStates(StatesGroup):
    waiting_for_game_id = State()
    waiting_for_receipt = State()

class UserMessageStates(StatesGroup):
    waiting_for_user_message = State()
    waiting_for_admin_reply = State()

# === MENYULAR ===
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎮 PUBG UC", callback_data="pubg_uc"),
        InlineKeyboardButton("💬 Adminga xabar", callback_data="admin_xabar"),
        InlineKeyboardButton("💰 UC narxlari", callback_data="uc_narx"),
        InlineKeyboardButton("ℹ️ Ma'lumotlar", callback_data="malumot"),
        InlineKeyboardButton("🧩 Akkaunt savdo", callback_data="akavideo")
    )
    return markup

def admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 Karta raqam", callback_data="set_card"),
        InlineKeyboardButton("➕ UC qo‘shish", callback_data="add_uc"),
        InlineKeyboardButton("❌ UC o‘chirish", callback_data="delete_uc"),
        InlineKeyboardButton("🎥 Ma'lumot videolar", callback_data="set_malumot"),
        InlineKeyboardButton("🎮 Akkaunt videolar", callback_data="set_akavideo"),
        InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")
    )
    return markup

def uc_list_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    if not data["uc_options"]:
        markup.add(InlineKeyboardButton("UC ro‘yxati yo‘q", callback_data="none"))
    else:
        for i, uc in enumerate(data["uc_options"]):
            markup.add(InlineKeyboardButton(f"{uc['label']} — {uc['price']}", callback_data=f"buy_{i}"))
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    return markup

# === START ===
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
        "Shohjaxon UC sotib olish botiga xush kelibsiz!",
        reply_markup=main_menu()
    )

# === ADMIN KIRISH ===
@dp.message_handler(commands=['admin'])
async def admin_login(message: types.Message):
    if message.from_user.id == ADMIN_ID or message.from_user.id in authorized_admins:
        await message.answer("✅ Siz admin sifatida tizimdasiz.", reply_markup=admin_panel())
    else:
        await message.answer("🔑 Admin parolini kiriting:")
        await AdminStates.waiting_for_password.set()

@dp.message_handler(state=AdminStates.waiting_for_password)
async def check_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        authorized_admins.add(message.from_user.id)
        await message.answer("✅ Parol to‘g‘ri, admin panelga xush kelibsiz!", reply_markup=admin_panel())
    else:
        await message.answer("❌ Noto‘g‘ri parol!")
    await state.finish()

# === ASOSIY MENYUGA QAYTISH ===
@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main_menu(call: types.CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    await call.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await call.answer()

# === UC QO‘SHISH / O‘CHIRISH / KARTA ===
@dp.callback_query_handler(lambda c: c.data == "set_card")
async def set_card_start(call: types.CallbackQuery):
    if call.from_user.id not in authorized_admins and call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    await call.message.answer("💳 Karta raqamini yuboring:")
    await AdminStates.waiting_for_card_number.set()

@dp.message_handler(state=AdminStates.waiting_for_card_number)
async def set_card_number(message: types.Message, state: FSMContext):
    data["admin_card"] = message.text.strip()
    save_data(data)
    await message.answer("✅ Karta saqlandi!", reply_markup=admin_panel())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "add_uc")
async def add_uc_start(call: types.CallbackQuery):
    if call.from_user.id not in authorized_admins and call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    await call.message.answer("➕ Yangi UC narxini kiriting (Masalan: 60 UC: 12 000 so‘m):")
    await AdminStates.waiting_for_add_uc.set()

@dp.message_handler(state=AdminStates.waiting_for_add_uc)
async def add_uc_price(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if ":" not in text:
        await message.answer("❌ Noto‘g‘ri format. Masalan: 60 UC: 12 000 so‘m")
        return
    label, price = text.split(":", 1)
    data["uc_options"].append({"label": label.strip(), "price": price.strip()})
    save_data(data)
    await message.answer("✅ UC qo‘shildi!", reply_markup=admin_panel())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "delete_uc")
async def delete_uc_start(call: types.CallbackQuery):
    if not data["uc_options"]:
        await call.message.answer("⚠️ UC ro‘yxati bo‘sh.")
        return
    markup = InlineKeyboardMarkup()
    for i, uc in enumerate(data["uc_options"]):
        markup.add(InlineKeyboardButton(f"❌ {uc['label']}", callback_data=f"remove_uc_{i}"))
    markup.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main"))
    await call.message.answer("O‘chirmoqchi bo‘lgan UC ni tanlang:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("remove_uc_"))
async def remove_uc(call: types.CallbackQuery):
    index = int(call.data.split("_")[2])
    if 0 <= index < len(data["uc_options"]):
        removed = data["uc_options"].pop(index)
        save_data(data)
        await call.message.answer(f"🗑 O‘chirildi: {removed['label']}")
    await call.message.answer("✅ UC ro‘yxati yangilandi!", reply_markup=admin_panel())

# === BUYURTMA TIZIMI ===
@dp.callback_query_handler(lambda c: c.data == "pubg_uc")
async def show_uc_list(call: types.CallbackQuery):
    await call.message.answer("💰 UC variantlardan birini tanlang:", reply_markup=uc_list_markup())
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def handle_buy_uc(call: types.CallbackQuery, state: FSMContext):
    idx = int(call.data.split("_")[1])
    selected_uc = data["uc_options"][idx]
    await state.update_data(selected_uc=selected_uc)
    await call.message.answer(
        f"📦 Siz tanladingiz: <b>{selected_uc['label']} — {selected_uc['price']}</b>\n\n"
        f"💳 To‘lov kartasi: <code>{data['admin_card']}</code>\n\n"
        "🎮 O‘yindagi ID raqamingizni kiriting:",
        parse_mode="HTML"
    )
    await OrderStates.waiting_for_game_id.set()
    await call.answer()

@dp.message_handler(state=OrderStates.waiting_for_game_id)
async def get_game_id(message: types.Message, state: FSMContext):
    await state.update_data(game_id=message.text)
    await message.answer("📸 To‘lov chek rasmini yuboring:")
    await OrderStates.waiting_for_receipt.set()

@dp.message_handler(content_types=['photo'], state=OrderStates.waiting_for_receipt)
async def receive_receipt(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    selected_uc = data_state.get("selected_uc")
    game_id = data_state.get("game_id")

    caption = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 @{message.from_user.username or message.from_user.full_name}\n"
        f"🎮 O‘yin ID: <code>{game_id}</code>\n"
        f"💰 Tanlangan UC: {selected_uc['label']} — {selected_uc['price']}"
    )

    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode="HTML")
    await message.answer("✅ Buyurtmangiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()

# === VIDEOLAR (20 TAGACHA) ===
async def show_video_with_next(message, category, index):
    videos = data["malumot_videos"] if category == "malumot" else data["akavideos"]
    markup = InlineKeyboardMarkup()
    if index + 1 < len(videos):
        markup.add(InlineKeyboardButton("▶️ Keyingi", callback_data=f"next_{category}_{index+1}"))
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    await message.answer_video(videos[index], caption=f"{category.title()} video {index+1}/{len(videos)}", reply_markup=markup)

# Ma’lumot video yuklash
@dp.callback_query_handler(lambda c: c.data == "set_malumot")
async def ask_malumot_video(call: types.CallbackQuery):
    await call.message.answer("🎥 1–20 tagacha ma’lumot videolarini yuboring (birma-bir).")
    await AdminStates.waiting_for_malumot_video.set()

@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_malumot_video)
async def save_malumot_video(message: types.Message):
    if len(data["malumot_videos"]) >= 20:
        await message.answer("⚠️ 20 ta video limiti to‘ldi!")
        return
    data["malumot_videos"].append(message.video.file_id)
    save_data(data)
    await message.answer(f"🎬 Video qo‘shildi ({len(data['malumot_videos'])}/20).", reply_markup=admin_panel())

@dp.callback_query_handler(lambda c: c.data == "malumot")
async def show_malumot(call: types.CallbackQuery):
    if not data["malumot_videos"]:
        await call.message.answer("⚠️ Ma’lumot videolari mavjud emas.")
        return
    await show_video_with_next(call.message, "malumot", 0)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("next_malumot_"))
async def next_malumot_video(call: types.CallbackQuery):
    index = int(call.data.split("_")[2])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await show_video_with_next(call.message, "malumot", index)
    await call.answer()

# Akkaunt video yuklash
@dp.callback_query_handler(lambda c: c.data == "set_akavideo")
async def ask_akavideo(call: types.CallbackQuery):
    await call.message.answer("🎮 1–20 tagacha akkaunt savdo videolarini yuboring (birma-bir).")
    await AdminStates.waiting_for_akavideo.set()

@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_akavideo)
async def save_akavideo(message: types.Message):
    if len(data["akavideos"]) >= 20:
        await message.answer("⚠️ 20 ta video limiti to‘ldi!")
        return
    data["akavideos"].append(message.video.file_id)
    save_data(data)
    await message.answer(f"🎮 Video qo‘shildi ({len(data['akavideos'])}/20).", reply_markup=admin_panel())

@dp.callback_query_handler(lambda c: c.data == "akavideo")
async def show_akavideo(call: types.CallbackQuery):
    if not data["akavideos"]:
        await call.message.answer("⚠️ Akkaunt videolari mavjud emas.")
        return
    await show_video_with_next(call.message, "akavideo", 0)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("next_akavideo_"))
async def next_akavideo_video(call: types.CallbackQuery):
    index = int(call.data.split("_")[2])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await show_video_with_next(call.message, "akavideo", index)
    await call.answer()

# === ADminga xabar yozish va javob ===
@dp.callback_query_handler(lambda c: c.data == "admin_xabar")
async def ask_user_message(call: types.CallbackQuery):
    await call.message.answer("💬 Xabaringizni yozing, u adminga yuboriladi.")
    await UserMessageStates.waiting_for_user_message.set()
    await call.answer()

@dp.message_handler(state=UserMessageStates.waiting_for_user_message, content_types=['text', 'photo', 'video'])
async def forward_to_admin(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✍️ Javob yozish", callback_data=f"reply_{message.from_user.id}"))
    if message.text:
        await bot.send_message(ADMIN_ID, f"📩 @{message.from_user.username or message.from_user.full_name} yozdi:\n\n{message.text}", reply_markup=markup)
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📷 @{message.from_user.username or message.from_user.full_name} dan rasm", reply_markup=markup)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=f"🎥 @{message.from_user.username or message.from_user.full_name} dan video", reply_markup=markup)
    await message.answer("✅ Xabaringiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def admin_reply(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return
    user_id = int(call.data.split("_")[1])
    await state.update_data(reply_user_id=user_id)
    await call.message.answer("✍️ Javobingizni kiriting:")
    await UserMessageStates.waiting_for_admin_reply.set()
    await call.answer()

@dp.message_handler(state=UserMessageStates.waiting_for_admin_reply, content_types=['text', 'photo', 'video'])
async def admin_send_reply(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    user_id = data_state["reply_user_id"]
    if message.text:
        await bot.send_message(user_id, f"💬 Admin javobi:\n{message.text}")
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id, caption="📷 Admin javobi")
    elif message.video:
        await bot.send_video(user_id, message.video.file_id, caption="🎥 Admin javobi")
    await message.answer("✅ Javob yuborildi!", reply_markup=admin_panel())
    await state.finish()

# === ISHGA TUSHIRISH ===
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



Meng malumot vdyo qoʻygandan soʻnga boshqa vdyo qoʻymaymanda lekin 20 ta vdyo qoʻy deyopti va qoʻysam orqaga qaytmayopti keyin akavunt savdoham shunqa boʻlyapti
Shuni menga toʻgʻirlab ber 
