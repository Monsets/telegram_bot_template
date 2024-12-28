import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery

from services.logger import log_event, log_error
from config.config import SUBSCRIPTION_PLANS
from database.db_operations import create_subscription

router = Router()

# Payment provider token from @BotFather
PROVIDER_TOKEN = 'your_provider_token'

# Message shown before invoice
PAYMENT_MESSAGE = """
💫 Thank you for choosing our subscription!

Plan: {title}
Price: {price} stars
Duration: {description}

You will be redirected to the payment page.
"""

@router.callback_query(F.data.startswith("sub_"))
async def send_invoice(callback: CallbackQuery):
    """
    Send payment invoice to user
    Triggered when user selects subscription option
    """
    user_id = callback.from_user.id
    try:
        log_event(user_id, "payment_start")
        sub_type = callback.data.split("_")[1]
        plan = SUBSCRIPTION_PLANS[sub_type]

        title = plan["title"]
        description = plan["description"]
        payload = f"subscription_{sub_type}"
        currency = "XTR"
        price = plan["price"]

        prices = [LabeledPrice(label="Subscription", amount=price)]

        # Обновляем текущее сообщение вместо его удаления
        await callback.message.edit_text(
            PAYMENT_MESSAGE.format(
                title=title,
                price=price,
                description=description
            )
        )
        
        # Отправляем инвойс отдельным сообщением
        await callback.bot.send_invoice(
            chat_id=user_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=PROVIDER_TOKEN,
            currency=currency,
            prices=prices
        )
        
        await callback.answer()
        
    except Exception as e:
        log_error(user_id, e, "send_invoice_error")
        await callback.message.answer("Sorry, something went wrong. Please try again later.")

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Answer pre-checkout query"""
    user_id = pre_checkout_query.from_user.id
    try:
        log_event(user_id, "payment_pre_checkout")
        await pre_checkout_query.answer(ok=True)
    except Exception as e:
        log_error(user_id, e, "pre_checkout_error")
        await pre_checkout_query.answer(ok=False, error_message="Payment processing error")

@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """
    Handle successful payment
    Creates subscription in database and sends confirmation to user
    """
    user_id = message.from_user.id
    try:
        # Get subscription type from payload
        sub_type = message.successful_payment.invoice_payload.split("_")[1]
        plan = SUBSCRIPTION_PLANS[sub_type]
        
        log_event(user_id, f"payment_success_{sub_type}")

        # Calculate subscription dates
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=plan["days"])

        # Create subscription in database
        await create_subscription(
            user_id=user_id,
            subscription_type=sub_type,
            start_date=start_date,
            end_date=end_date
        )

        # Send confirmation message
        await message.answer(
            f"Thank you for your payment!\n"
            f"Your {plan['title']} is now active.\n"
            f"Valid until: {end_date.strftime('%Y-%m-%d')}"
        )
    except Exception as e:
        log_error(user_id, e, "payment_success_processing_error")
        await message.answer("Payment received, but there was an error activating your subscription. Our support team will contact you.")
