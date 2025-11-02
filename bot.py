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

# === Global o‘zgaruvchilar ===
uc_options = []  # UC variantlari
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


class OrderStates(StatesGroup):
    waiting_for_game_id = State()
    waiting_for_receipt = State()


class UserMessageStates(StatesGroup):
    waiting_for_user_message = State()
    waiting_for_admin_reply = State()


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


# === Start komandasi ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
                         "Shoxjaxon UC sotib olish botiga xush kelibsiz!", reply_markup=main_menu())


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
    global admin_card, uc_options, malumot_video, akavideo

    data = call.data
    user_id = call.from_user.id

    # 🔙 Asosiy menyu
    if data == "back_to_main":
        await call.message.answer("🏠 Asosiy menyu", reply_markup=main_menu())
        await call.answer()
        return

    # 🎮 PUBG UC
    if data == "pubg_uc":
        if uc_options:
            await call.message.answer("💰 UC variantlardan birini tanlang:", reply_markup=uc_list_markup())
        else:
            await call.message.answer("❌ UC narxlari hali kiritilmagan.", reply_markup=main_menu())
        await call.answer()
        return

    # 💬 Adminga yozish
    if data == "admin_xabar":
        await call.message.answer("💬 Adminga yubormoqchi bo‘lgan xabaringizni yozing:")
        await UserMessageStates.waiting_for_user_message.set()
        await call.answer()
        return

    # 💰 UC narxlari
    if data == "uc_narx":
        if uc_options:
            text = "\n".join([f"🔹 {uc['label']} — {uc['price']}" for uc in uc_options])
            await call.message.answer(f"💰 UC narxlari:\n{text}")
        else:
            await call.message.answer("❌ UC narxlari hali belgilanmagan.")
        await call.answer()
        return

    # ℹ️ Ma'lumot video
    if data == "malumot":
        if malumot_video:
            await call.message.answer_video(malumot_video, caption="ℹ️ UC haqida ma'lumot:")
        else:
            await call.message.answer("🎞 Ma'lumot videosi hali yo‘q.")
        await call.answer()
        return

    # 🧩 Akkaunt video
    if data == "akavideo":
        if akavideo:
            await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo videosi:")
        else:
            await call.message.answer("📹 Akkaunt savdo videosi hali yo‘q.")
        await call.answer()
        return

    # 💳 Admin karta va UC narx belgilash
    if data == "set_uc" and user_id == ADMIN_ID:
        await call.message.answer("💳 Karta raqamini kiriting:")
        await AdminStates.waiting_for_card_number.set()
        await call.answer()
        return

    # ➕ UC qo‘shish
    if data == "add_uc" and user_id == ADMIN_ID:
        await call.message.answer("➕ UC variantini kiriting (masalan):\n660 UC: 12 000 so‘m")
        await AdminStates.waiting_for_add_uc.set()
        await call.answer()
        return

    # ❌ UC o‘chirish
    if data == "delete_uc" and user_id == ADMIN_ID:
        if not uc_options:
            await call.message.answer("❌ UC ro‘yxati bo‘sh.")
            return
        text = "O‘chirmoqchi bo‘lgan UC raqamini kiriting:\n"
        for i, uc in enumerate(uc_options, 1):
            text += f"{i}. {uc['label']} — {uc['price']}\n"
        await call.message.answer(text)
        await AdminStates.waiting_for_delete_uc.set()
        await call.answer()
        return

    # 🎥 Ma'lumot video
    if data == "set_malumot" and user_id == ADMIN_ID:
        await call.message.answer("🎥 Ma'lumot videosini yuboring:")
        await AdminStates.waiting_for_malumot_video.set()
        await call.answer()
        return

    # 🎮 Akkaunt video
    if data == "set_akavideo" and user_id == ADMIN_ID:
        await call.message.answer("🎮 Akkaunt videosini yuboring:")
        await AdminStates.waiting_for_akavideo.set()
        await call.answer()
        return

    # 🛒 UC sotib olish
    if data.startswith("buy_"):
        idx = int(data.split("_")[1])
        if idx < len(uc_options):
            await state.update_data(selected_idx=idx)
            option = uc_options[idx]
            await call.message.answer(f"💳 To‘lovni quyidagi karta raqamiga yuboring:\n\n{admin_card}\n\n"
                                      f"Tanlangan UC: {option['label']} — {option['price']}\n\n"
                                      "🔢 Endi o‘yin ID raqamingizni kiriting:")
            await OrderStates.waiting_for_game_id.set()
        await call.answer()
        return


# === Buyurtma olish ===
@dp.message_handler(state=OrderStates.waiting_for_game_id)
async def process_game_id(message: types.Message, state: FSMContext):
    await state.update_data(game_id=message.text)
    await message.answer("📸 Endi to‘lov chekini yuboring:")
    await OrderStates.waiting_for_receipt.set()


@dp.message_handler(content_types=['photo'], state=OrderStates.waiting_for_receipt)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("selected_idx")
    game_id = data.get("game_id")
    option = uc_options[idx]
    caption = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 @{message.from_user.username}\n"
        f"📦 {option['label']} — {option['price']}\n"
        f"🎮 O‘yin ID: {game_id}\n"
        f"🆔 Telegram ID: {message.from_user.id}"
    )
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Buyurtmangiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()


# === Admin UC va karta ===
@dp.message_handler(state=AdminStates.waiting_for_card_number)
async def set_card_number(message: types.Message, state: FSMContext):
    global admin_card
    admin_card = message.text.strip()
    await message.answer("✅ Karta raqami saqlandi. Endi UC narxlarini kiriting:\nMasalan:\n660 UC: 12 000 so‘m, 1320 UC: 24 000 so‘m")
    await AdminStates.waiting_for_uc_price.set()


@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def set_uc_prices(message: types.Message, state: FSMContext):
    global uc_options
    parts = [p.strip() for p in message.text.split(",") if ":" in p]
    uc_options = [{"label": p.split(":")[0].strip(), "price": p.split(":")[1].strip()} for p in parts]
    await message.answer("✅ UC narxlar saqlandi!", reply_markup=admin_panel())
    await state.finish()


@dp.message_handler(state=AdminStates.waiting_for_add_uc)
async def add_uc(message: types.Message, state: FSMContext):
    global uc_options
    try:
        label, price = message.text.split(":")
        uc_options.append({"label": label.strip(), "price": price.strip()})
        await message.answer(f"✅ {label.strip()} — {price.strip()} qo‘shildi!", reply_markup=admin_panel())
    except:
        await message.answer("❌ Noto‘g‘ri format! Masalan: 660 UC: 12 000 so‘m")
    await state.finish()


@dp.message_handler(state=AdminStates.waiting_for_delete_uc)
async def delete_uc(message: types.Message, state: FSMContext):
    global uc_options
    try:
        idx = int(message.text) - 1
        if 0 <= idx < len(uc_options):
            deleted = uc_options.pop(idx)
            await message.answer(f"🗑 {deleted['label']} o‘chirildi!", reply_markup=admin_panel())
        else:
            await message.answer("❌ Bunday raqamli UC mavjud emas.")
    except:
        await message.answer("❌ Iltimos, raqam kiriting.")
    await state.finish()


# === Video kiritish ===
@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_malumot_video)
async def set_malumot_video(message: types.Message, state: FSMContext):
    global malumot_video
    malumot_video = message.video.file_id
    await message.answer("🎥 Ma'lumot videosi saqlandi!", reply_markup=admin_panel())
    await state.finish()


@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_akavideo)
async def set_akavideo(message: types.Message, state: FSMContext):
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
        await bot.send_message(ADMIN_ID, f"📩 @{message.from_user.username} yozdi:\n\n{message.text}", reply_markup=markup)
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📷 @{message.from_user.username} dan xabar", reply_markup=markup)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=f"🎥 @{message.from_user.username} dan video", reply_markup=markup)
    await message.answer("✅ Xabaringiz adminga yuborildi!", reply_markup=main_menu())
    await state.finish()


# === Admin javobi ===
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
