import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = "8568223587:AAEHaVPFcfvb-T03vsY4bcaT6jYHuRai66c"
ADMIN_ID = 7973934849  # Admin Telegram ID-ni shu yerga yozing

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# === Global o‘zgaruvchilar ===
uc_options = []  # Har bir element: {"label": "660 UC", "price": "12 000 so‘m"}
malumot_video = None
akavideo = None
admin_card = None

# === Holatlar ===
class AdminStates(StatesGroup):
    waiting_for_uc_price = State()
    waiting_for_card_number = State()
    waiting_for_add_uc = State()
    waiting_for_delete_uc = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()


# === Menyular ===
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
        InlineKeyboardButton("💸 UC narxni belgilash", callback_data="set_uc"),
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
        markup.add(InlineKeyboardButton("UC ro‘yxati bo‘sh", callback_data="none"))
    else:
        for i, uc in enumerate(uc_options):
            markup.add(InlineKeyboardButton(f"{uc['label']} — {uc['price']}", callback_data=f"buy_{i}"))
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    return markup


# === Start komandasi ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("👋 Assalomu alaykum!\nUC sotib olish botiga xush kelibsiz!", reply_markup=main_menu())


# === Admin komandasi ===
@dp.message_handler(commands=['admin'])
async def admin_panel_open(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ Admin paneli:", reply_markup=admin_panel())
    else:
        await message.answer("⛔ Siz admin emassiz.")


# === Callbacklar ===
@dp.callback_query_handler(lambda c: c.data)
async def callback_router(call: types.CallbackQuery, state: FSMContext):
    global admin_card, uc_options

    data = call.data
    user_id = call.from_user.id

    # 🔙 Asosiy menyu
    if data == "back_to_main":
        await call.message.answer("🏠 Asosiy menyu", reply_markup=main_menu())
        await call.answer()
        return

    # 🔹 Admin UC narx belgilash
    if data == "set_uc":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
            return
        await call.message.answer("💳 Karta raqamini kiriting:")
        await AdminStates.waiting_for_card_number.set()
        await call.answer()
        return

    # ➕ UC qo‘shish
    if data == "add_uc":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
            return
        await call.message.answer("➕ UC variantini kiriting (masalan):\n\n660 UC: 12 000 so‘m")
        await AdminStates.waiting_for_add_uc.set()
        await call.answer()
        return

    # ❌ UC o‘chirish
    if data == "delete_uc":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
            return
        if not uc_options:
            await call.message.answer("❌ Hozircha UC ro‘yxati bo‘sh.")
            return
        text = "O‘chirmoqchi bo‘lgan UC variantining raqamini kiriting:\n"
        for i, uc in enumerate(uc_options, 1):
            text += f"{i}. {uc['label']} — {uc['price']}\n"
        await call.message.answer(text)
        await AdminStates.waiting_for_delete_uc.set()
        await call.answer()
        return

    # 🎮 Foydalanuvchi uchun UC ro‘yxati
    if data == "pubg_uc":
        if uc_options:
            await call.message.answer("💰 Mavjud UC variantlari:", reply_markup=uc_list_markup())
        else:
            await call.message.answer("❌ UC ro‘yxati bo‘sh.", reply_markup=main_menu())
        await call.answer()
        return


# === UC qo‘shish ===
@dp.message_handler(state=AdminStates.waiting_for_add_uc)
async def add_uc_option(message: types.Message, state: FSMContext):
    global uc_options
    try:
        label, price = message.text.split(":")
        uc_options.append({"label": label.strip(), "price": price.strip()})
        await message.answer(f"✅ {label.strip()} — {price.strip()} qo‘shildi!", reply_markup=admin_panel())
    except:
        await message.answer("❌ Noto‘g‘ri format! To‘g‘ri yozing: 660 UC: 12 000 so‘m")
    await state.finish()


# === UC o‘chirish ===
@dp.message_handler(state=AdminStates.waiting_for_delete_uc)
async def delete_uc_option(message: types.Message, state: FSMContext):
    global uc_options
    try:
        index = int(message.text) - 1
        if 0 <= index < len(uc_options):
            deleted = uc_options.pop(index)
            await message.answer(f"🗑 {deleted['label']} o‘chirildi!", reply_markup=admin_panel())
        else:
            await message.answer("❌ Bunday raqamli UC mavjud emas.")
    except ValueError:
        await message.answer("❌ Iltimos, raqam kiriting.")
    await state.finish()


# === Admin karta raqamini kiritish ===
@dp.message_handler(state=AdminStates.waiting_for_card_number)
async def set_card_number(message: types.Message, state: FSMContext):
    global admin_card
    admin_card = message.text.strip()
    await message.answer("✅ Karta raqami saqlandi! Endi UC narxlarini kiriting:\n\nMasalan:\n660 UC: 12 000 so‘m, 1320 UC: 24 000 so‘m")
    await AdminStates.waiting_for_uc_price.set()


# === UC narxlarini kiritish ===
@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def set_uc_prices(message: types.Message, state: FSMContext):
    global uc_options
    parts = [p.strip() for p in message.text.split(",") if ":" in p]
    uc_options = [{"label": p.split(":")[0].strip(), "price": p.split(":")[1].strip()} for p in parts]
    await message.answer("✅ UC narxlar yangilandi!", reply_markup=admin_panel())
    await state.finish()


# === Buyurtma berish ===
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def handle_buy(call: types.CallbackQuery, state: FSMContext):
    global admin_card
    idx = int(call.data.split("_")[1])
    if idx >= len(uc_options):
        await call.answer("❌ Xatolik!", show_alert=True)
        return
    option = uc_options[idx]
    text = f"💳 To‘lovni quyidagi karta raqamiga yuboring:\n\n{admin_card}\n\n" \
           f"Tanlangan UC: {option['label']} — {option['price']}\n\n" \
           f"✅ To‘lovdan so‘ng o‘yin ID va chekni yuboring."
    await call.message.answer(text)
    await call.answer()


# === Xatoliklar uchun ===
@dp.errors_handler()
async def errors_handler(update, error):
    print(f"Xatolik: {error}")
    return True


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
