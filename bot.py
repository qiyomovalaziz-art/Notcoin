import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8471383666:AAH75KlVq2XPYqRd0JYbLuWB5yRUHM6oyWc'  # <-- BotFather dan token
ADMIN_ID = 123456789  # <-- Adminning Telegram ID si

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Ma'lumotlarni vaqtincha saqlash
uc_narxlar = "UC narxlari hali belgilanmagan."
malumot_video = None
akavideo = None


# --- Asosiy menyu ---
def main_menu():
    buttons = [
        [InlineKeyboardButton("🎮 PUBG UC", callback_data='uc')],
        [InlineKeyboardButton("💬 Adminga xabar", callback_data='admin_xabar')],
        [InlineKeyboardButton("💰 UC narxlari", callback_data='uc_narx')],
        [InlineKeyboardButton("ℹ️ Ma'lumotlar", callback_data='malumot')],
        [InlineKeyboardButton("🧩 Akkaunt savdo", callback_data='akavunt')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Admin paneli ---
def admin_panel():
    buttons = [
        [InlineKeyboardButton("💸 UC narxni o'zgartirish", callback_data='set_uc')],
        [InlineKeyboardButton("🎥 Ma'lumot video qo'yish", callback_data='set_malumot')],
        [InlineKeyboardButton("🎮 Akkaunt video qo'yish", callback_data='set_akavideo')],
        [InlineKeyboardButton("⬅️ Asosiy menyu", callback_data='back_to_main')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = f"👋 Assalomu alaykum, {message.from_user.first_name}!\n" \
           f"Shoxjaxon UC sotib olish botiga xush kelibsiz!"
    await message.answer(text, reply_markup=main_menu())


# --- UC buyurtma shakli uchun holatlar ---
class UcForm(StatesGroup):
    waiting_for_id = State()
    waiting_for_miqdor = State()
    waiting_for_screenshot = State()


# --- UC tugmasi bosilganda ---
@dp.callback_query_handler(lambda c: c.data == 'uc')
async def start_uc_order(call: types.CallbackQuery):
    await call.message.answer("🆔 Iltimos, o‘yin ichidagi ID raqamingizni yuboring:")
    await UcForm.waiting_for_id.set()


@dp.message_handler(state=UcForm.waiting_for_id)
async def get_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("💰 Necha UC sotib olmoqchisiz? (Masalan: 660 UC)")
    await UcForm.waiting_for_miqdor.set()


@dp.message_handler(state=UcForm.waiting_for_miqdor)
async def get_miqdor(message: types.Message, state: FSMContext):
    await state.update_data(miqdor=message.text)
    await message.answer("📸 To‘lov chekini (skrinshot) rasm sifatida yuboring:")
    await UcForm.waiting_for_screenshot.set()


@dp.message_handler(content_types=['photo'], state=UcForm.waiting_for_screenshot)
async def get_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    miqdor = data['miqdor']

    # Adminga yuboriladi
    caption = (
        f"🆕 Yangi UC buyurtma!\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 O‘yin ID: {user_id}\n"
        f"💰 Miqdor: {miqdor}\n"
        f"🕓 Telegram ID: {message.from_user.id}"
    )

    photo = message.photo[-1].file_id
    await bot.send_photo(ADMIN_ID, photo, caption=caption)

    await message.answer("✅ Buyurtmangiz qabul qilindi! Tez orada admin siz bilan bog‘lanadi.", reply_markup=main_menu())
    await state.finish()


# --- Boshqa tugmalar ---
@dp.callback_query_handler(lambda c: True)
async def inline_menu(call: types.CallbackQuery):
    global uc_narxlar, malumot_video, akavideo

    if call.data == 'admin_xabar':
        await call.message.answer("📩 Adminga yozish uchun: @username")

    elif call.data == 'uc_narx':
        await call.message.answer(f"💰 UC narxlari:\n\n{uc_narxlar}")

    elif call.data == 'malumot':
        if malumot_video:
            await call.message.answer_video(malumot_video, caption="ℹ️ UC haqida ma’lumot videosi:")
        else:
            await call.message.answer("🎞 Hozircha video mavjud emas.")
    
    elif call.data == 'akavunt':
        if akavideo:
            await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo videosi:")
        else:
            await call.message.answer("📹 Akkaunt savdo videolari hali qo‘shilmagan.")

    elif call.data == 'back_to_main':
        await call.message.edit_text("🏠 Asosiy menyu", reply_markup=main_menu())

    elif call.data.startswith('set_') and call.from_user.id != ADMIN_ID:
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)


# --- Admin komandasi ---
@dp.message_handler(commands=['admin'])
async def admin_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ Admin paneli", reply_markup=admin_panel())
    else:
        await message.answer("Siz admin emassiz.")


# --- Admin sozlamalari uchun holatlar ---
class AdminStates(StatesGroup):
    waiting_for_uc_price = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()


@dp.callback_query_handler(lambda c: c.data == 'set_uc')
async def set_uc_price_btn(call: types.CallbackQuery):
    if call.from_user.id == ADMIN_ID:
        await call.message.answer("💸 Yangi UC narxlarini kiriting:")
        await AdminStates.waiting_for_uc_price.set()


@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def set_uc_price(message: types.Message, state: FSMContext):
    global uc_narxlar
    uc_narxlar = message.text
    await message.answer("✅ UC narxlari yangilandi!", reply_markup=admin_panel())
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'set_malumot')
async def set_malumot_btn(call: types.CallbackQuery):
    if call.from_user.id == ADMIN_ID:
        await call.message.answer("🎥 Ma'lumot uchun video yuboring:")
        await AdminStates.waiting_for_malumot_video.set()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_malumot_video)
async def set_malumot_vid(message: types.Message, state: FSMContext):
    global malumot_video
    malumot_video = message.video.file_id
    await message.answer("🎥 Ma'lumot videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'set_akavideo')
async def set_akavideo_btn(call: types.CallbackQuery):
    if call.from_user.id == ADMIN_ID:
        await call.message.answer("🎮 Akkaunt savdo uchun video yuboring:")
        await AdminStates.waiting_for_akavideo.set()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_akavideo)
async def set_akavideo_vid(message: types.Message, state: FSMContext):
    global akavideo
    akavideo = message.video.file_id
    await message.answer("🎮 Akkaunt video saqlandi!", reply_markup=admin_panel())
    await state.finish()


# --- Botni ishga tushirish ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
