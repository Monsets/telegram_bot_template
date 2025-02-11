import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from services.logger import log_event, log_error
from database.db_operations import get_active_subscription
from keyboards.keyboards import subscription_kb, profile_kb

from config.config import SUBSCRIPTION_PLANS, REFERRAL_BONUS_DAYS

router = Router()

@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    """Handle /subscription command"""
    try:
        user_id = message.from_user.id
        log_event(user_id, "subscription_menu")
        
        await message.answer(
            "Enhance your experience with our subscription plans:",
            reply_markup=subscription_kb
        )
        
    except Exception as e:
        log_error(message.from_user.id, e, "subscription_command_error")
        await message.answer("Error showing subscription plans. Please try again later.")

@router.callback_query(F.data == "show_sub")
async def show_subscription_status(callback: CallbackQuery):
    """Show current subscription status"""
    user_id = callback.from_user.id
    try:
        log_event(user_id, "subscription_status_check")
        await callback.message.edit_reply_markup(reply_markup=None)
        subscription = await get_active_subscription(user_id)
        
        if subscription:
            days_left = (subscription.end_date - datetime.datetime.now()).days
            plan = SUBSCRIPTION_PLANS.get(subscription.subscription_type, {})
            price = plan.get('price', 'N/A')
            
            log_event(user_id, "subscription_status_active")
            await callback.message.answer(
                f"Your subscription status:\n\n"
                f"Plan: {plan.get('title', subscription.subscription_type)}\n"
                f"Price: {price} stars\n"
                f"Valid until: {subscription.end_date.strftime('%Y-%m-%d')}\n"
                f"Days left: {days_left}"
            )
        else:
            log_event(user_id, "subscription_status_inactive")
            await callback.message.answer(
                "You don't have an active subscription.\n"
                "Use /subscription to view available plans."
            )
        
        await callback.answer()
        
    except Exception as e:
        log_error(user_id, e, "subscription_status_error")
        await callback.answer("Error checking subscription status", show_alert=True)

@router.callback_query(F.data == "buy_sub")
async def buy_subscription(callback: CallbackQuery):
    """Show subscription plans"""
    try:
        log_event(callback.from_user.id, "buy_subscription_from_profile")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()
        await cmd_subscription(callback.message)
    except Exception as e:
        log_error(callback.from_user.id, e, "buy_subscription_error")
        await callback.answer("Error opening subscription menu", show_alert=True)

@router.callback_query(F.data == "cancel_sub")
async def cancel_subscription(callback: CallbackQuery):
    """Handle subscription cancellation"""
    user_id = callback.from_user.id
    try:
        log_event(user_id, "subscription_cancellation_request")
        await callback.message.edit_reply_markup(reply_markup=None)
        subscription = await get_active_subscription(user_id)
        
        if subscription:
            # TODO: Add subscription cancellation logic here
            log_event(user_id, "subscription_cancellation_info_shown")
            cancel_text = [
                "ℹ️ Subscription Cancellation",
                "",
                "To cancel your subscription, please contact our support:",
                "• Email: support@example.com",
                "• Telegram: @support_bot",
                "",
                "Please include your User ID in the message:",
                f"User ID: {user_id}",
                "",
                "Your subscription will remain active until the end date."
            ]
            
            await callback.message.answer("\n".join(cancel_text))
        else:
            log_event(user_id, "subscription_cancellation_no_active")
            await callback.message.answer(
                "You don't have an active subscription to cancel."
            )
        
        await callback.answer()
        
    except Exception as e:
        log_error(user_id, e, "subscription_cancellation_error")
        await callback.answer("Error canceling subscription", show_alert=True)

@router.callback_query(F.data == "return_to_profile")
async def return_to_profile(callback: CallbackQuery):
    """Return to profile menu"""
    try:
        await callback.message.edit_reply_markup(reply_markup=profile_kb)
        await callback.answer()
    except Exception as e:
        log_error(callback.from_user.id, e, "return_to_profile_error")
        await callback.answer("Error returning to profile", show_alert=True)
