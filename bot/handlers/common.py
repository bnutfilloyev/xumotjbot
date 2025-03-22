from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb, remove_kb
from structures.database import db
from structures.states import RegState
from structures.subscription_checking import check_subscription, send_subscription_prompt
from handlers.nomination import show_nominations_markup

start_router = Router()


@start_router.message(Command("start"))
async def start_command(
    message: types.Message, state: FSMContext, bot: Bot
):
    """Start command."""
    user_data = {
        "username": message.from_user.username,
        "fullname": message.from_user.full_name,
    }

    user_info = await db.user_update(user_id=message.from_user.id, data=user_data)

    if user_info.get("input_fullname") is None:
        text = "📝 Botdan to'liq foydalanish uchun avval ro'yxatdan o'tishingiz kerak. Iltimos, ism va familiyangizni kiriting:"
        await message.answer(text=text, reply_markup=remove_kb())
        return await state.set_state(RegState.fullname)

    if user_info.get("input_phone") is None:
        text = "📞 Iltimos, telefon raqamingizni kiriting. Biz siz bilan bog'lanishimiz uchun bu muhim!"
        await message.answer(text=text, reply_markup=contact_kb())
        return await state.set_state(RegState.phone_number)

    if not await check_subscription(bot, message.from_user.id):
        await send_subscription_prompt(message, bot)
        return

    await show_nominations_markup(message)


@start_router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if await check_subscription(bot, callback.from_user.id):
        await callback.message.edit_text("✅ Tabriklaymiz! Obunangiz muvaffaqiyatli tasdiqlandi!")

        await show_nominations_markup(callback.message)
    else:
        await callback.answer("❌ Afsuski, siz hali ham kanalga obuna bo'lmagansiz. Iltimos, obuna bo'lib yana bir bor urinib ko'ring!", show_alert=True)