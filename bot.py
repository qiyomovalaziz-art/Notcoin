import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = "BOT_TOKENINGIZNI_BU_YERGA_QOYING"  # Bot token
ADMIN_ID = 123456789  # Admin Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- Saqlanadigan ma'lumotlar (dastlab bo'sh yoki matnli) ---
# uc_options — admin tomonidan o'rnatiladigan variantlar ro'yxati: [{'label':'660','price':'12 000 soʻm'}, ...]
uc_options = []        # boshida bo'sh — admin to'ldiradi
uc_narxlar_text = "UC narxlari hali belgilanmagan."  # fallback matn

malumot_video = None
akavideo = None


# --- Menyular ---
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


# --- Start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n"
        f"Shoxjaxon UC sotib olish botiga xush kelibsiz!",
        reply_markup=main_menu()
    )


# --- Admin command to open admin panel ---
@dp.message_handler(commands=['admin'])
async def admin_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ Admin paneli", reply_markup=admin_panel())
    else:
        await message.answer("⛔ Siz admin emassiz.")


# --- Order FSM (foydalanuvchi buyurtmasi) ---
class OrderStates(StatesGroup):
    waiting_for_selected = State()       # holds selected option index
    waiting_for_game_id = State()
    waiting_for_card = State()
    waiting_for_receipt = State()


# --- Admin FSM (sozlashlar) ---
class AdminStates(StatesGroup):
    waiting_for_uc_price = State()
    waiting_for_malumot_video = State()
    waiting_for_akavideo = State()


# --- Helper: build inline keyboard from uc_options ---
def build_uc_options_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    if uc_options:
        for idx, opt in enumerate(uc_options):
            # callback data: buy_<index>
            text = f"{opt['label']} — {opt['price']}"
            markup.insert(InlineKeyboardButton(text, callback_data=f"buy_{idx}"))
    else:
        # fallback single button that shows fallback text
        markup.insert(InlineKeyboardButton("UC narxlari (yo'q)", callback_data="uc_empty"))
    # also a back to main button
    markup.add(InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="back_to_main"))
    return markup


# --- Callback handler (barcha callbacklarni shu yerda ushlab olamiz) ---
@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    global uc_narxlar_text, malumot_video, akavideo

    data = call.data
    user_id = call.from_user.id

    # --- Back to main ---
    if data == "back_to_main":
        # use answer and send main menu as a new message to avoid edit errors (works on both inline and normal)
        await call.message.answer("🏠 Asosiy menyu", reply_markup=main_menu())
        await call.answer()
        return

    # --- Show UC options when user presses PUBG UC ---
    if data == "pubg_uc":
        # If admin set options, show them; otherwise show fallback text
        if uc_options:
            await call.message.answer("🔹 UC variantlardan birini tanlang:", reply_markup=build_uc_options_markup())
        else:
            await call.message.answer(f"💰 {uc_narxlar_text}\n\nAdmin panelidan narxlar kiritilmagan.", reply_markup=main_menu())
        await call.answer()
        return

    # --- User chose a UC option: callback starts with buy_  ---
    if data.startswith("buy_"):
        idx_str = data.split("_", 1)[1]
        try:
            idx = int(idx_str)
            # store selected index in FSM data and ask for Game ID
            await state.update_data(selected_idx=idx)
            await call.message.answer("🆔 Iltimos, o‘yin ichidagi ID raqamingizni yuboring:")
            await OrderStates.waiting_for_game_id.set()
        except Exception:
            await call.message.answer("Xato: variant topilmadi.")
        await call.answer()
        return

    # --- If no UC options set and user presses uc_empty ---
    if data == "uc_empty":
        await call.message.answer(f"💰 {uc_narxlar_text}\n\nAdmin panelidan narxlar kiritilmagan.", reply_markup=main_menu())
        await call.answer()
        return

    # --- UC prices quick view ---
    if data == "uc_narx":
        if uc_options:
            text = "💰 UC narxlari:\n"
            for opt in uc_options:
                text += f"{opt['label']} — {opt['price']}\n"
            await call.message.answer(text, reply_markup=main_menu())
        else:
            await call.message.answer(f"💰 {uc_narxlar_text}", reply_markup=main_menu())
        await call.answer()
        return

    # --- Ma'lumot video show ---
    if data == "malumot":
        if malumot_video:
            await call.message.answer_video(malumot_video, caption="ℹ️ UC haqida ma'lumot:")
        else:
            await call.message.answer("🎞 Ma'lumot videosi hali qo‘shilmagan.")
        await call.answer()
        return

    # --- Akkaunt savdo video ---
    if data == "akavideo":
        if akavideo:
            await call.message.answer_video(akavideo, caption="🎮 Akkaunt savdo:")
        else:
            await call.message.answer("📹 Akkaunt savdo videosi hali qo‘shilmagan.")
        await call.answer()
        return

    # --- Adminga xabar (foydalanuvchiga admin userni ko'rsatish) ---
    if data == "admin_xabar":
        await call.message.answer("📩 Adminga yozish uchun: @your_admin_username_here")
        await call.answer()
        return

    # === ADMIN ACTIONS (faqat adminga ruxsat) ===
    if data == "set_uc":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Sizga bu funksiya ruxsat etilmagan!", show_alert=True)
            return
        await call.message.answer("💸 UC narxlarini kiriting (format):\n\n660:12 000 soʻm, 1320:24 000 soʻm\n\nHar bir variantni `label:price` ko'rinishida vergul bilan ajrating.")
        await AdminStates.waiting_for_uc_price.set()
        await call.answer()
        return

    if data == "set_malumot":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Sizga bu funksiya ruxsat etilmagan!", show_alert=True)
            return
        await call.message.answer("🎥 Ma'lumot videosini yuboring (video fayl):")
        await AdminStates.waiting_for_malumot_video.set()
        await call.answer()
        return

    if data == "set_akavideo":
        if user_id != ADMIN_ID:
            await call.answer("⛔ Sizga bu funksiya ruxsat etilmagan!", show_alert=True)
            return
        await call.message.answer("🎮 Akkaunt videosini yuboring (video fayl):")
        await AdminStates.waiting_for_akavideo.set()
        await call.answer()
        return

    # default fallback
    await call.answer()


# --- Order FSM handlers: Game ID, Card number, Receipt photo ---
@dp.message_handler(state=OrderStates.waiting_for_game_id)
async def process_game_id(message: types.Message, state: FSMContext):
    # Save game ID and ask for card/account number
    await state.update_data(game_id=message.text)
    await message.answer("💳 Iltimos to‘lov uchun karta (yoki hisob) raqamini yuboring:")
    await OrderStates.waiting_for_card.set()


@dp.message_handler(state=OrderStates.waiting_for_card)
async def process_card(message: types.Message, state: FSMContext):
    await state.update_data(card=message.text)
    await message.answer("📸 To‘lov chekini (skrinshot/rasm) yuboring:")
    await OrderStates.waiting_for_receipt.set()


@dp.message_handler(content_types=['photo'], state=OrderStates.waiting_for_receipt)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sel_idx = data.get("selected_idx")
    game_id = data.get("game_id")
    card = data.get("card")
    # get option text
    if sel_idx is not None and 0 <= int(sel_idx) < len(uc_options):
        opt = uc_options[int(sel_idx)]
        selected_text = f"{opt['label']} — {opt['price']}"
    else:
        selected_text = uc_narxlar_text

    caption = (
        f"🆕 Yangi UC buyurtma!\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📦 Variant: {selected_text}\n"
        f"🆔 O'yin ID: {game_id}\n"
        f"💳 Karta/Hisob: {card}\n"
        f"🕓 Telegram ID: {message.from_user.id}"
    )

    # send photo with caption to admin
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Buyurtmangiz adminga yuborildi. Tez orada bog'lanadi.", reply_markup=main_menu())
    await state.finish()


# --- Admin handlers: set prices (parsing), set videos ---
@dp.message_handler(state=AdminStates.waiting_for_uc_price)
async def admin_set_uc_price(message: types.Message, state: FSMContext):
    global uc_options, uc_narxlar_text
    text = message.text.strip()
    parsed = []
    # parse pattern: parts separated by comma, each part like "660:12 000 so'm"
    try:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for p in parts:
            if ":" in p:
                label, price = p.split(":", 1)
                parsed.append({'label': label.strip(), 'price': price.strip()})
            else:
                # if no colon, treat whole as a label with empty price
                parsed.append({'label': p, 'price': ''})
        if parsed:
            uc_options = parsed
            # update fallback text for safety
            uc_narxlar_text = "  ".join([f"{o['label']} — {o['price']}" for o in uc_options])
            await message.answer("✅ UC variantlari yangilandi!", reply_markup=admin_panel())
        else:
            uc_options = []
            uc_narxlar_text = text
            await message.answer("✅ UC narxlari yangilandi (oddiy matn).", reply_markup=admin_panel())
    except Exception:
        uc_options = []
        uc_narxlar_text = text
        await message.answer("✅ UC narxlari yangilandi (oddiy matn).", reply_markup=admin_panel())

    await state.finish()


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


# --- Run bot ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
