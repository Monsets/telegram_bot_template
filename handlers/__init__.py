from aiogram import Dispatcher
from .base import router as base_router
from .profile import router as profile_router
from .subscription import router as subscription_router
from .payments import router as payment_router
from .channel_reader import router as channel_router

def register_all_handlers(dp: Dispatcher, config):
    """
    Register all handlers in correct order
    """
    dp.include_router(base_router)
    dp.include_router(profile_router)
    dp.include_router(subscription_router)
    dp.include_router(payment_router)
    dp.include_router(channel_router)
