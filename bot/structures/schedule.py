from aiogram import Bot, types
from configuration import conf
from structures.broadcaster import send_message


async def on_startup(bot: Bot) -> None:
    """Actions that need to be completed before the bot starts"""
    for admin in conf.bot.admins:
        await send_message(
            user_id=admin, text="Bot ishga tushdi ✅", keyboard=None, bot=bot
        )
    await bot.delete_my_commands()
    commands = [
        types.BotCommand(command="start", description="🚀 Botni ishga tushurish"),
        types.BotCommand(command="help", description="🆘 Yordam"),
    ]
    await bot.set_my_commands(commands=commands)
