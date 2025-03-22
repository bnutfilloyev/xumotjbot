from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.common_kb import nominations_kb, participants_kb, NominationCallback, ParticipantCallback
from structures.database import db

router = Router()

async def show_nominations_markup(message: Message):
    nominations = await db.get_nominations()
    
    if not nominations:
        return await message.answer("📋 Hozirda hech qanday faol nominatsiya mavjud emas. Tez orada yangilanishlarni kuting!")

    
    btn = await nominations_kb(nominations)
    await message.answer(
        "🏆 Ovoz berib, sevimli ishtirokchingizni qo'llab-quvvatlang! Quyidagi nominatsiyalardan birini tanlang:",
        reply_markup=btn
    )

@router.callback_query(NominationCallback.filter())
async def show_participants(query: CallbackQuery, callback_data: NominationCallback):
    await query.answer()
    
    nomination_id = callback_data.id
    nomination = await db.get_nomination(nomination_id)
    
    if not nomination:
        await query.message.edit_text("❗️Kechirasiz, bu nominatsiya topilmadi. Iltimos, boshqa nominatsiyani tanlang.")
        return
    
    participants = await db.get_participants(nomination_id)

    
    await query.message.edit_text(
        f"📣 '{nomination['title']}' nominatsiyasida ishtirok etayotganlar:\n"
        f"👇 Quyidagi ishtirokchilardan biriga ovoz bering va g'olibni aniqlashga yordam bering:",
        reply_markup=await participants_kb(participants, nomination_id)
    )

@router.callback_query(F.data == "back_to_nominations")
async def back_to_nominations(query: CallbackQuery):
    """Return to the nominations list"""
    await query.answer()
    nominations = await db.get_nominations()

    btn = await nominations_kb(nominations)
    await query.message.edit_text("🔙 Asosiy ro'yxatga qaytib, yana bir nominatsiyani tanlang yoki sevimli ishtirokchingiz uchun ovoz bering:", reply_markup=btn)

@router.callback_query(ParticipantCallback.filter())
async def vote_for_participant(query: CallbackQuery, callback_data: ParticipantCallback):
    # await query.answer()

    user_id = query.from_user.id
    nomination_id = callback_data.nomination_id
    participant_name = callback_data.name
    
    # Record the vote using the proper parameters
    success, result_text = await db.add_vote(
        nomination_id=nomination_id,
        participant_name=participant_name, 
        user_id=user_id
    )
    
    if success:
        await query.answer(text=f"🎯 Ajoyib tanlov! {participant_name} uchun ovozingiz muvaffaqiyatli qabul qilindi. \n\n{result_text}", show_alert=True)
        
        btn = await nominations_kb(nominations=await db.get_nominations())
        await query.message.edit_text("📜 Yana boshqa nominatsiyalarga ham ovoz bering va sevimli ishtirokchingizga yordam bering!", reply_markup=btn)
        return

    if not success:
        await query.answer(f"❌ Afsuski, ovoz berish amalga oshmadi: {result_text}", show_alert=True)
        
        nomination = await db.get_nomination(nomination_id)

        if nomination:
            participants = await db.get_participants(nomination_id)
            
            await query.message.edit_text(
                f"🔍 '{nomination['title']}' nominatsiyasida yana kimlar borligini ko'rib chiqing va eng munosibiga ovoz bering:",
                reply_markup=await participants_kb(participants, nomination_id)
            )
        else:
            # If nomination not found, just show all nominations
            nominations = await db.get_nominations()
            await query.message.edit_text(
                "📋 Quyidagi nominatsiyalardan birini tanlang:",
                reply_markup=await nominations_kb(nominations)
            )