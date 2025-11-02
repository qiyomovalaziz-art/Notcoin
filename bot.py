import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = "8568223587:AAEHaVPFcfvb-T03vsY4bcaT6jYHuRai66c"
ADMIN_ID = 7973934849  # Admin Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Saqlanadigan ma'lumotlar
uc_options = []
uc_narxlar_text = "UC narxlari hali belgilanmagan."
malumot_video = None
akavideo = None
admin_card = None  # Admin kiritgan karta raqami

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
        InlineKeyboardButton("💸 UC narxni o‘zgartirish", callback_data="set_uc"),
        InlineKeyboardButton("🎥 Ma'lumot video", callback_data="set_malumot"),
        InlineKeyboardButton("🎮 Akkaunt video", callback_data="set_akavideo"),
        InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main")
    )
    return markup


# === Holatlar ===
class OrderStates(StatesGroup):
    waiting_for_selected = State()
    waiting_for_game_id = State()
    waiting_for_card = State()
    waiting_for_receipt = State()


class AdminStates(StatesGroup):
    waiting_for_uc_price = State()
    waiting_for_card_number = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()


class UserMessageStates(StatesGroup):
    waiting_for_user_message = State()
    waiting_for_admin_reply = State()


# === Start ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
        f"Shoxjaxon UC sotib olish botiga xush kelibsiz!",
        reply_markup=main_menu()
    )


@dp.message_handler(commands=['admin'])
async def admin_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ Admin paneli", reply_markup=admin_panel())
    else:
        await message.answer("⛔ Siz admin emassiz.")


# === UC menyu ===
def build_uc_options_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    if uc_options:
        for idx, opt in enumerate(uc_options):
            text = f"{opt['label']} — {opt['price']}"
            markup.insert(InlineKeyboardButton(text, callback_data=f"buy_{idx}"))
    else:
        markup.insert(InlineKeyboardButton("UC narxlari (yo‘q)", callback_data="uc_empty"))
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    return markup


# === Callbacklar ===
@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    global uc_narxlar_text, malumot_video, akavideo, admin_card

    data = call.data
    user_id = call.from_user.id

    if data == "back_to_main":
        await call.message.answer("🏠 Asosiy menyu", reply_markup=main_menu())
        await call.answer()
        return

    if data == "pubg_uc":
        if uc_options:
            await call.message.answer("🔹 UC variantlardan birini tanlang:", reply_markup=build_uc_options_markup())
        else:
            await call.message.answer(f"💰 {uc_narxlar_text}\n\nAdmin hali narx kiritmagan.", reply_markup=main_menu())
        await call.answer()
        return

    if data.startswith("buy_"):
        idx = int(data.split("_")[1])
        await state.update_data(selected_idx=idx)
        if admin_card:
            await call.message.answer(f"💳 To‘lovni quyidagi karta raqamiga yuboring:\n\n{admin_card}")
        await call.message.answer("🆔 Iltimos, o‘yin ichidagi ID raqamingizni yuboring:")
        await OrderStates.waiting_for_game_id.set()
        await call.answer()
        return

    if data == "uc_empty":
        await call.message.answer(f"💰 {uc_narxlar_text}", reply_markup=main_menu())
        await call.answer()
        return

    if data == "uc_narx":
        if uc_options:
            text = "💰 UC narxlari:\n" + "\n".join([f"{o['label']} — {o['price']}" for o in uc_options])
            await call.message.answer(text, reply_markup=main_menu())
        else:
            await call.message.answer(uc_narxlar_text, reply_markup=main_menu())
        await call.answer()
        return

    if data == "malumot":
        if malumot_video:
            await call.message.answer_video(malumot_video, caption="ℹ️ UC haqida ma'lumot:")
        else:
            await call.message.answer("🎞 Ma'lumot videosi hali qo‘shilmagan.")
        await call.answer()
        return

    if data == "akavideo":
        if akavideo:
            await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo:")
        else:
            await call.message.answer("📹 Akkaunt savdo videosi hali yo‘q.")
        await call.answer()
        return

    if data == "admin_xabar":
        await call.message.answer("💬 Xabaringizni kiriting (matn, rasm yoki video bo‘lishi mumkin):")
        await UserMessageStates.waiting_for_user_message.set()
        await call.answer()
        return

    if data == "set_uc":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
            return
        await call.message.answer("💸 UC narxlarini kiriting (masalan):\n660:12 000 so‘m, 1320:24 000 so‘m")
        await AdminStates.waiting_for_uc_price.set()
        await call.answer()
        return

    if data == "set_malumot":
        if user_id == ADMIN_ID:
            await call.message.answer("🎥 Ma'lumot videosini yuboring:")
            await AdminStates.waiting_for_malumot_video.set()
        else:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
        return

    if data == "set_akavideo":
        if user_id == ADMIN_ID:
            await call.message.answer("🎮 Akkaunt videosini yuboring:")
            await AdminStates.waiting_for_akavideo.set()
        else:
            await call.answer("⛔ Ruxsat yo‘q!", show_alert=True)
        return


# === Buyurtma bosqichlari ===
@dp.message_handler(state=OrderStates.waiting_for_game_id)
async def process_game_id(message: types.Message, state: FSMContext):
    await state.update_data(game_id=message.text)
    await message.answer("📸 Iltimos, to‘lov chekini yuboring:")
    await OrderStates.waiting_for_receipt.set()


@dp.message_handler(content_types=['photo'], state=OrderStates.waiting_for_receipt)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sel_idx = data.get("selected_idx")
    game_id = data.get("game_id")

    opt = uc_options[sel_idx] if sel_idx is not None and sel_idx < len(uc_options) else {"label": "?", "price": "?"}
    caption = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📦 {opt['label']} — {opt['price']}\n"
        f"🆔 O‘yin ID: {game_id}\n"
        f"💳 Telegram ID: {message.from_user.id}"
    )

    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Buyurtma adminga yuborildi!", reply_markup=main_menu())
    await state.finish()


# === Admin UC narx va karta ===
@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def admin_set_uc_price(message: types.Message, state: FSMContext):
    global uc_options
    parts = [p.strip() for p in message.text.split(",") if ":" in p]
    uc_options = [{"label": p.split(":")[0].strip(), "price": p.split(":")[1].strip()} for p in parts]
    await message.answer("💳 Endi karta raqamini yuboring:")
    await AdminStates.waiting_for_card_number.set()


@dp.message_handler(state=AdminStates.waiting_for_card_number)
async def admin_set_card_number(message: types.Message, state: FSMContext):
    global admin_card
    admin_card = message.text.strip()
    await message.answer("✅ Karta raqami va UC narxlar saqlandi!", reply_markup=admin_panel())
    await state.finish()


# === Video saqlash ===
@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_malumot_video)
async def admin_set_malumot_video(message: types.Message, state: FSMContext):
    global malumot_video
    malumot_video = message.video.file_id
    await message.answer("🎥 Ma'lumot videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_akavideo)
async def admin_set_akavideo(message: types.Message, state: FSMContext):
    global akavideo
    akavideo = message.video.file_id
    await message.answer("🎮 Akkaunt videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


# === Foydalanuvchidan adminga xabar ===
@dp.message_handler(state=UserMessageStates.waiting_for_user_message, content_types=['text', 'photo', 'video'])
async def forward_to_admin(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✍️ Javob yozish", callback_data=f"reply_{message.from_user.id}")
    )
    if message.text:
        await bot.send_message(ADMIN_ID, f"💬 Yangi xabar:\n{message.text}\n\n👤 @{message.from_user.username}", reply_markup=markup)
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📷 Xabar @{message.from_user.username}", reply_markup=markup)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=f"🎥 Xabar @{message.from_user.username}", reply_markup=markup)

    await message.answer("✅ Xabaringiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()


# === Admin foydalanuvchiga javob ===
@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def start_admin_reply(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return
    user_id = int(call.data.split("_")[1])
    await state.update_data(reply_user_id=user_id)
    await call.message.answer("✍️ Javobingizni kiriting (matn, rasm yoki video):")
    await UserMessageStates.waiting_for_admin_reply.set()
    await call.answer()


@dp.message_handler(state=UserMessageStates.waiting_for_admin_reply, content_types=['text', 'photo', 'video'])
async def admin_send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_user_id")

    if message.text:
        await bot.send_message(user_id, f"💬 Admin javobi:\n{message.text}")
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id, caption="📷 Admindan rasm")
    elif message.video:
        await bot.send_video(user_id, message.video.file_id, caption="🎥 Admin video yubordi")

    await message.answer("✅ Javob yuborildi!")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
