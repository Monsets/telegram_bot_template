from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from config.config import SUBSCRIPTION_PLANS

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    buttons = [
        [
            KeyboardButton(text="👤 Profile"),
            KeyboardButton(text="📊 Subscription")
        ],
        [KeyboardButton(text="ℹ️ Help")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Choose an option"
    )

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Create subscription options keyboard"""
    buttons = []
    
    # Create buttons from subscription plans
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan.get('is_referral'):
            buttons.append([
                InlineKeyboardButton(
                    text=f"{plan['title']} - Free!",
                    callback_data="referral_sub"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{plan['title']} - {plan['price']}⭐",
                    callback_data=f"sub_{plan_id}"
                )
            ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Create profile menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📊 Subscription Status", callback_data="show_sub")],
        [InlineKeyboardButton(text="💫 Buy Subscription", callback_data="buy_sub")],
        [InlineKeyboardButton(text="❌ Cancel Subscription", callback_data="cancel_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Create keyboard instances
main_kb = get_main_keyboard()
profile_kb = get_profile_keyboard()
subscription_kb = get_subscription_keyboard()
