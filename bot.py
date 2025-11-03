import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

# === TOKEN & ADMIN SOZLAMALAR ===
API_TOKEN = "8568223587:AAEHaVPFcfvb-T03vsY4bcaT6jYHuRai66c"
ADMIN_ID = 7823588220
ADMIN_PASSWORD = "shoh123"  # <-- bu parolni o'zgartiring

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# === GLOBAL O‘ZGARUVCHILAR ===
uc_options = []
malumot_video = None
akavideo = None
admin_card = None
authorized_admins = set()

# === HOLATLAR ===
class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_uc_price = State()
    waiting_for_card_number = State()
    waiting_for_add_uc = State()
    waiting_for_delete_uc = State()
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
        InlineKeyboardButton("💳 Karta va UC narxni belgilash", callback_data="set_uc"),
        InlineKeyboardButton("➕ UC qo‘shish", callback_data="add_uc"),
        InlineKeyboardButton("❌ UC o‘chirish", callback_data="delete_uc"),
        InlineKeyboardButton("🎥 Ma'lumot video", callback_data="set_malumot"),
        InlineKeyboardButton("🎮 Akkaunt video", callback_data="set_akavideo"),
        InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")
    )
    return markup


def uc_list_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    if not uc_options:
        markup.add(InlineKeyboardButton("UC ro‘yxati yo‘q", callback_data="none"))
    else:
        for i, uc in enumerate(uc_options):
            markup.add(InlineKeyboardButton(f"{uc['label']} — {uc['price']}", callback_data=f"buy_{i}"))
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    return markup


# === /start KOMANDASI ===
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
        "Shohjaxon UC sotib olish botiga xush kelibsiz!",
        reply_markup=main_menu()
    )


# === /admin PAROL TEKSHIRISH ===
@dp.message_handler(commands=['admin'])
async def admin_login(message: types.Message):
    if message.from_user.id == ADMIN_ID or message.from_user.id in authorized_admins:
        await message.answer("🔐 Siz allaqachon admin sifatida tizimdasiz!", reply_markup=admin_panel())
        return
    await message.answer("🔑 Admin parolini kiriting:")
    await AdminStates.waiting_for_password.set()


@dp.message_handler(state=AdminStates.waiting_for_password)
async def check_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        authorized_admins.add(message.from_user.id)
        await message.answer("✅ Muvaffaqiyatli kirdingiz!", reply_markup=admin_panel())
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


# === PUBG UC RO‘YXATI ===
@dp.callback_query_handler(lambda c: c.data == "pubg_uc")
async def show_uc_options(call: types.CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    await call.message.answer("💰 UC variantlardan birini tanlang:", reply_markup=uc_list_markup())
    await call.answer()


# === UC TANLASH ===
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def handle_buy_uc(call: types.CallbackQuery, state: FSMContext):
    idx = int(call.data.split("_")[1])
    selected_uc = uc_options[idx]
    await state.update_data(selected_uc=selected_uc)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(
        f"📦 Siz tanladingiz: <b>{selected_uc['label']} — {selected_uc['price']}</b>\n\n"
        f"💳 To‘lov kartasi: <code>{admin_card}</code>\n\n"
        "Iltimos, o‘yindagi ID raqamingizni kiriting:",
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
    data = await state.get_data()
    selected_uc = data.get("selected_uc")
    game_id = data.get("game_id")

    caption = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 @{message.from_user.username or message.from_user.full_name}\n"
        f"🎮 O‘yin ID: <code>{game_id}</code>\n"
        f"💰 Tanlangan UC: {selected_uc['label']} — {selected_uc['price']}"
    )

    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode="HTML")
    await message.answer("✅ Buyurtmangiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()


# === ADMIN PANEL FUNKSIYALARI ===
@dp.callback_query_handler(lambda c: c.data == "set_uc")
async def set_uc_start(call: types.CallbackQuery):
    if call.from_user.id not in authorized_admins and call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer("💳 Karta raqamini yuboring:")
    await AdminStates.waiting_for_card_number.set()


@dp.message_handler(state=AdminStates.waiting_for_card_number)
async def set_card_number(message: types.Message, state: FSMContext):
    global admin_card
    admin_card = message.text.strip()
    await message.answer("✅ Karta saqlandi.\nEndi UC narxlarini kiriting:\nMasalan: 60 UC: 12 000 so‘m, 120 UC: 24 000 so‘m")
    await AdminStates.waiting_for_uc_price.set()


@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def set_uc_prices(message: types.Message, state: FSMContext):
    global uc_options
    parts = [p.strip() for p in message.text.split(",") if ":" in p]
    uc_options = [{"label": p.split(":")[0].strip(), "price": p.split(":")[1].strip()} for p in parts]
    await message.answer("✅ UC narxlar saqlandi!", reply_markup=admin_panel())
    await state.finish()


# === VIDEO YUKLASH ===
@dp.callback_query_handler(lambda c: c.data == "set_malumot")
async def ask_malumot_video(call: types.CallbackQuery):
    if call.from_user.id not in authorized_admins and call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer("🎥 Ma'lumot videosini yuboring:")
    await AdminStates.waiting_for_malumot_video.set()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_malumot_video)
async def set_malumot_video_func(message: types.Message, state: FSMContext):
    global malumot_video
    malumot_video = message.video.file_id
    await message.answer("🎥 Ma'lumot videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "set_akavideo")
async def ask_akavideo(call: types.CallbackQuery):
    if call.from_user.id not in authorized_admins and call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer("🎮 Akkaunt videosini yuboring:")
    await AdminStates.waiting_for_akavideo.set()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_akavideo)
async def set_akavideo_func(message: types.Message, state: FSMContext):
    global akavideo
    akavideo = message.video.file_id
    await message.answer("🎮 Akkaunt videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


# === VIDEO KO‘RSATISH (FOYDALANUVCHI UCHUN) ===
@dp.callback_query_handler(lambda c: c.data == "malumot")
async def show_malumot(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    if malumot_video:
        await call.message.answer_video(malumot_video, caption="ℹ️ Ma'lumot videosi")
    else:
        await call.message.answer("⚠️ Hozircha ma'lumot video mavjud emas.")
    await call.message.answer("⬅️ Asosiy menyu", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")))
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "akavideo")
async def show_akavideo(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    if akavideo:
        await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo videosi")
    else:
        await call.message.answer("⚠️ Akkaunt video hali yuklanmagan.")
    await call.message.answer("⬅️ Asosiy menyu", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")))
    await call.answer()


# === ADMIN-XABAR MULOQOT ===
@dp.callback_query_handler(lambda c: c.data == "admin_xabar")
async def ask_user_message(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer("💬 Xabaringizni yozing, u adminga yuboriladi.")
    await UserMessageStates.waiting_for_user_message.set()
    await call.answer()


@dp.message_handler(state=UserMessageStates.waiting_for_user_message, content_types=['text', 'photo', 'video'])
async def forward_to_admin(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✍️ Javob yozish", callback_data=f"reply_{message.from_user.id}"))
    if message.text:
        await bot.send_message(ADMIN_ID, f"📩 @{message.from_user.username} yozdi:\n\n{message.text}", reply_markup=markup)
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📷 @{message.from_user.username} dan xabar", reply_markup=markup)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=f"🎥 @{message.from_user.username} dan video", reply_markup=markup)
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
    data = await state.get_data()
    user_id = data["reply_user_id"]
    if message.text:
        await bot.send_message(user_id, f"💬 Admin javobi:\n{message.text}")
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id, caption="📷 Admin javobi")
    elif message.video:
        await bot.send_video(user_id, message.video.file_id, caption="🎥 Admin javobi")
    await message.answer("✅ Javob yuborildi!", reply_markup=admin_panel())
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
