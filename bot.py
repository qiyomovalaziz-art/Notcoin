import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = "8471383666:AAH75KlVq2XPYqRd0JYbLuWB5yRUHM6oyWc"  # Bot token
ADMIN_ID = 7973934849  # Admin Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- O'zgaruvchilar ---
uc_narxlar = "💰 UC narxlari hali kiritilmagan."
malumot_video = None
akavideo = None


# --- Asosiy menyu ---
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


# --- Admin menyu ---
def admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💸 UC narxni o‘zgartirish", callback_data="set_uc"),
        InlineKeyboardButton("🎥 Ma'lumot video", callback_data="set_malumot"),
        InlineKeyboardButton("🎮 Akkaunt video", callback_data="set_akavideo"),
        InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")
    )
    return markup


# --- START komandasi ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
        f"Shoxjaxon UC sotib olish botiga xush kelibsiz!",
        reply_markup=main_menu()
    )


# --- ADMIN komandasi ---
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ Admin paneli", reply_markup=admin_panel())
    else:
        await message.answer("⛔ Siz admin emassiz.")


# --- ADMIN holatlari ---
class AdminState(StatesGroup):
    waiting_for_uc_price = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()


# --- Callback handler ---
@dp.callback_query_handler(lambda call: True)
async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    global uc_narxlar, malumot_video, akavideo

    data = call.data

    # --- Asosiy menyu ---
    if data == "back_to_main":
        await call.message.edit_text("🏠 Asosiy menyu", reply_markup=main_menu())

    # --- UC narxlari ---
    elif data == "uc_narx":
        await call.message.answer(f"💰 UC narxlari:\n\n{uc_narxlar}")

    # --- Ma'lumot video ---
    elif data == "malumot":
        if malumot_video:
            await call.message.answer_video(malumot_video, caption="ℹ️ UC haqida ma’lumot videosi:")
        else:
            await call.message.answer("🎞 Ma'lumot videosi hali qo‘shilmagan.")

    # --- Akkaunt savdo video ---
    elif data == "akavideo":
        if akavideo:
            await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo videosi:")
        else:
            await call.message.answer("📹 Akkaunt savdo videosi hali qo‘shilmagan.")

    # --- Adminga xabar ---
    elif data == "admin_xabar":
        await call.message.answer("📩 Adminga yozish uchun: @username")

    # === ADMIN BO'LIM ===
    elif data == "set_uc" and call.from_user.id == ADMIN_ID:
        await call.message.answer("💸 Yangi UC narxlarini kiriting:")
        await AdminState.waiting_for_uc_price.set()

    elif data == "set_malumot" and call.from_user.id == ADMIN_ID:
        await call.message.answer("🎥 Ma'lumot videosini yuboring:")
        await AdminState.waiting_for_malumot_video.set()

    elif data == "set_akavideo" and call.from_user.id == ADMIN_ID:
        await call.message.answer("🎮 Akkaunt videosini yuboring:")
        await AdminState.waiting_for_akavideo.set()

    else:
        await call.answer("⛔ Sizga bu funksiya ruxsat etilmagan!", show_alert=True)


# --- UC narxini qabul qilish ---
@dp.message_handler(state=AdminState.waiting_for_uc_price)
async def set_uc_price(message: types.Message, state: FSMContext):
    global uc_narxlar
    uc_narxlar = message.text
    await message.answer("✅ UC narxlari yangilandi!", reply_markup=admin_panel())
    await state.finish()


# --- Ma'lumot videosini qabul qilish ---
@dp.message_handler(content_types=['video'], state=AdminState.waiting_for_malumot_video)
async def set_malumot_video(message: types.Message, state: FSMContext):
    global malumot_video
    malumot_video = message.video.file_id
    await message.answer("🎥 Ma'lumot videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


# --- Akkaunt videosini qabul qilish ---
@dp.message_handler(content_types=['video'], state=AdminState.waiting_for_akavideo)
async def set_akavideo_video(message: types.Message, state: FSMContext):
    global akavideo
    akavideo = message.video.file_id
    await message.answer("🎮 Akkaunt videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


# --- Run bot ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
