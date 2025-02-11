from datetime import datetime, timedelta
from database.db_operations import update_referral_count, create_subscription
from services.logger import log_event, log_error
from config.config import REFERRAL_BONUS_DAYS
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

async def process_referral(user_id: int, referrer_id: int) -> None:
    """Process referral and add bonus subscription to referrer"""
    try:
        # Update referrer's stats and give bonus
        await update_referral_count(referrer_id)
        log_event(user_id, f"referred_by_{referrer_id}")
        
        # Add bonus subscription days to referrer
        start_date = datetime.now()
        end_date = start_date + timedelta(days=REFERRAL_BONUS_DAYS)
        
        try:
            await create_subscription(
                user_id=referrer_id,
                subscription_type="referral_bonus",
                start_date=start_date,
                end_date=end_date
            )
            log_event(referrer_id, "referral_bonus_added")
        except Exception as e:
            log_error(referrer_id, e, "referral_bonus_error")
    except Exception as e:
        log_error(user_id, e, "referral_processing_error")
        raise

router = Router()

@router.callback_query(F.data == "referral_sub")
async def show_referral_info(callback: CallbackQuery):
    """Show referral subscription info"""
    try:
        user_id = callback.from_user.id
        log_event(user_id, "referral_subscription_info")
        
        bot_username = (await callback.bot.me()).username
        referral_link = f"t.me/{bot_username}?start={user_id}"
        
        referral_text = [
            "🎁 <b>Invite Friends - Get Free Subscription!</b>",
            "",
            f"• Get {REFERRAL_BONUS_DAYS} days for each invited friend",
            "• No limits on invites",
            "• Instant activation",
            "",
            "📲 Share your referral link:",
            f"{referral_link}"
        ]
        
        await callback.message.edit_text(
            "\n".join(referral_text)
        )
        await callback.answer()
        
    except Exception as e:
        log_error(user_id, e, "referral_info_error")
        await callback.answer("Error showing referral info", show_alert=True)