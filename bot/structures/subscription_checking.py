from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest
from configuration import conf

CHANNEL_ID = conf.bot.channel_id

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False


async def send_subscription_prompt(message: types.Message, bot: Bot):
    try:
        invite_link = await bot.create_chat_invite_link(CHANNEL_ID)
        
        text = (
            "📢 <b>Botdan foydalanish uchun avval quyidagi kanalga a'zo bo'lishingiz lozim.</b>\n"
            "⚡️ Bu orqali siz <i>yangiliklardan xabardor</i> bo'lasiz va <u>maxsus imkoniyatlarga ega</u> bo'lasiz! 🔥\n"
            f"<a href='{invite_link.invite_link}'>➡️ Kanalga o'tish</a>"
        )
        inline_kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔗 Kanalga ulanish", url=invite_link.invite_link)],
                [types.InlineKeyboardButton(text="🔍 Obunani tekshirish", callback_data="check_subscription")]
            ]
        )
        await message.answer(text, reply_markup=inline_kb, disable_web_page_preview=True, parse_mode="HTML")
        
    except TelegramBadRequest as e:
        channel_name = CHANNEL_ID.lstrip('@')
        text = (
            "📢 <b>Botdan foydalanish uchun quyidagi kanalga a'zo bo'lishingiz lozim.</b>\n"
            "⚡️ Bu orqali siz <i>yangiliklardan xabardor</i> bo'lasiz va <u>maxsus imkoniyatlarga ega</u> bo'lasiz! 🔥\n"
            f"<a href='https://t.me/{channel_name}'>➡️ Kanalga o'tish</a>"
        )
        inline_kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔗 Kanalga ulanish", url=f"https://t.me/{channel_name}")],
                [types.InlineKeyboardButton(text="🔍 Obunani tekshirish", callback_data="check_subscription")]
            ]
        )
        await message.answer(text, reply_markup=inline_kb, disable_web_page_preview=True, parse_mode="HTML")
