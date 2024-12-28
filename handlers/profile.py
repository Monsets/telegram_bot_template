from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.logger import log_event, log_error
from database.db_operations import get_user, get_active_subscription
from keyboards.keyboards import profile_kb
from datetime import datetime

router = Router()

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Handle /profile command"""
    user_id = message.from_user.id
    log_event(user_id, "profile_open")
    
    try:
        user = await get_user(user_id)
        if not user:
            await message.answer("Please start the bot first with /start")
            return
            
        subscription = await get_active_subscription(user_id)
        
        profile_text = [
            "👤 Your Profile:",
            f"ID: {user_id}",
            f"Name: {user.name or 'Not set'}",
            "\n📊 Subscription Status:"
        ]
        
        if subscription:
            days_left = (subscription.end_date - datetime.now()).days
            profile_text.extend([
                f"Type: {subscription.subscription_type}",
                f"Valid until: {subscription.end_date.strftime('%Y-%m-%d')}",
                f"Days left: {days_left}"
            ])
        else:
            profile_text.append("No active subscription")
        
        await message.answer(
            "\n".join(profile_text),
            reply_markup=profile_kb
        )
        
    except Exception as e:
        log_error(user_id, e, "profile_error")
        await message.answer("Error loading profile. Please try again later.") 