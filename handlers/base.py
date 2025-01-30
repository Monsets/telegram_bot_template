from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from services.logger import log_event, log_error
from database.db_operations import add_user, get_user, update_referral_count
from keyboards.keyboards import main_kb
from handlers.profile import cmd_profile as profile_command
from handlers.subscription import cmd_subscription as subscription_command

router = Router()

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
            # Create new user with referrer_id
            await add_user(
                user_id=user_id,
                username=message.from_user.username,
                name=message.from_user.full_name,
                referrer_id=referrer_id
            )
            log_event(user_id, "user_add")
            
            # If there's a referrer, increment their referral count
            if referrer_id:
                await update_referral_count(referrer_id)
                log_event(user_id, f"referred_by_{referrer_id}")
        
        welcome_text = [
            f"👋 Welcome, {message.from_user.full_name}!",
            "",
            "🎁 Invite friends and get rewards!",
            f"Your referral link: t.me/{(await message.bot.me()).username}?start={user_id}",
            "",
            "Use the menu below to navigate:"
        ]
        
        await message.answer(
            "\n".join(welcome_text),
            reply_markup=main_kb
        )
    except Exception as e:
        log_error(user_id, e, "start_command_error")
        await message.answer("Sorry, something went wrong. Please try again.")

# Handle keyboard buttons
@router.message(F.text == "👤 Profile")
async def profile_button(message: Message):
    """Handle Profile button press"""
    try:
        await profile_command(message)
    except Exception as e:
        log_error(message.from_user.id, e, "profile_button_error")
        await message.answer("Error opening profile")

@router.message(F.text == "📊 Subscription")
async def subscription_button(message: Message):
    """Handle Subscription button press"""
    try:
        await subscription_command(message)
    except Exception as e:
        log_error(message.from_user.id, e, "subscription_button_error")
        await message.answer("Error opening subscription menu")

@router.message(F.text == "ℹ️ Help")
async def help_button(message: Message):
    """Handle Help button press"""
    try:
        await cmd_help(message)
    except Exception as e:
        log_error(message.from_user.id, e, "help_button_error")
        await message.answer("Error showing help")

@router.message(Command("help"))
async def cmd_help(message: Message):
    log_event(message.from_user.id, "help")
    help_text = [
        "Available commands:",
        "/start - 👋 Start the bot",
        "/help - ℹ️ Show this help message",
        "/menu - 📱 Show main menu",
        "/profile - 👤 View your profile",
        "/subscription - 📊 View subscription plans"
    ]
    await message.answer("\n".join(help_text))

@router.message(Command("menu"))
async def show_menu(message: Message):
    """Show main menu keyboard"""
    await message.answer(
        "Main menu:",
        reply_markup=main_kb
    )
