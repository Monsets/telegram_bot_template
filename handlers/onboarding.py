from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from services.logger import log_event, log_error
from database.db_operations import add_user, get_user
from keyboards.keyboards import main_kb
from handlers.referral import process_referral
from config.config import REFERRAL_BONUS_DAYS

router = Router()

async def get_welcome_text(message: Message) -> str:
    """Generate welcome text with referral info"""
    return "\n".join([
        f"👋 Welcome, {message.from_user.full_name}!",
        "",
        "🎁 Invite friends and get rewards!",
        f"Your referral link: t.me/{(await message.bot.me()).username}?start={message.from_user.id}",
        f"Bonus for each friend: {REFERRAL_BONUS_DAYS} days of subscription",
        "",
        "Use the menu below to navigate:"
    ])

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    log_event(user_id, "start")
    
    try:
        # Extract referral code from deep link
        args = message.text.split()
        referrer_id = int(args[1]) if len(args) > 1 else None
        
        user = await get_user(user_id)
        if not user:
            # Create new user
            await add_user(
                user_id=user_id,
                username=message.from_user.username,
                name=message.from_user.full_name,
                referrer_id=referrer_id
            )
            log_event(user_id, "user_add")
            
            # Process referral if exists
            if referrer_id:
                await process_referral(user_id, referrer_id)
        
        # Show welcome text for both new and existing users
        welcome_text = await get_welcome_text(message)
        await message.answer(
            welcome_text,
            reply_markup=main_kb
        )
    except Exception as e:
        log_error(user_id, e, "start_command_error")
        await message.answer("Sorry, something went wrong. Please try again.")