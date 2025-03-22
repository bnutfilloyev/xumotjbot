from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class NominationCallback(CallbackData, prefix="nomination"):
    id: str
    name: str


class ParticipantCallback(CallbackData, prefix="participant"):
    nomination_id: str
    name: str


def remove_kb():
    return ReplyKeyboardRemove()


def contact_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="📲 Telefon raqamingizni kiriting yoki quyidagi tugmani bosing",
    )
    return keyboard


async def nominations_kb(nominations: list):
    builder = InlineKeyboardBuilder()
    
    for nomination in nominations:
        callback_data = NominationCallback(id=str(nomination['_id']), name=nomination['title']).pack()
        builder.button(text=f"🏆 {nomination['title']}", callback_data=callback_data)
    
    builder.adjust(1)
    
    return builder.as_markup()


async def participants_kb(participants: list, nomination_id: str = None):
    builder = InlineKeyboardBuilder()
    
    for participant in participants:
        participant_name = participant.get('name')
        votes = participant.get('votes', 0)
        
        callback_data = ParticipantCallback(nomination_id=str(nomination_id),name=participant_name).pack()
        
        builder.button(
            text=f"✨ {participant_name} — {votes} ta ovoz",
            callback_data=callback_data
        )
    
    builder.button(text="🔙 Nominatsiyalarga qaytish", callback_data="back_to_nominations")
    
    builder.adjust(1)
    
    return builder.as_markup()