from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb
from structures.states import RegState
from structures.database import db
from structures.subscription_checking import check_subscription, send_subscription_prompt
from handlers.nomination import show_nominations_markup

register_router = Router()


@register_router.message(RegState.fullname, ~F.text.startswith("/"))
async def input_firstname(message: types.Message, state: FSMContext):
    await state.update_data(input_fullname=message.text)
    text = "📲 Iltimos, telefon raqamingizni kiriting. Biz siz bilan bog'lanishimiz uchun bu muhim!"
    await message.answer(text=text, reply_markup=contact_kb())
    await state.set_state(RegState.phone_number)


@register_router.message(
    RegState.phone_number, ~F.text.startswith("/") | F.text | F.contact
)
async def input_phone(message: types.Message, state: FSMContext):
    """📞 Telefon raqamingiz qabul qilindi. Endi quyidagi ko'rsatmalarga amal qiling."""
    if message.contact:
        phone = message.contact.phone_number

    if message.text:
        phone = message.text

    await state.update_data(input_phone=phone)
    data = await state.get_data()
    await db.user_update(user_id=message.from_user.id, data=data)
    await state.clear()

    if not await check_subscription(message.bot, message.from_user.id):
        await send_subscription_prompt(message)
        return

    await message.answer("🎯 Sizning ro'yxatdan o'tishingiz muvaffaqiyatli yakunlandi! Endi ovoz berishda qatnashishingiz mumkin. ✅")
    await show_nominations_markup(message)
