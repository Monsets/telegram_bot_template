import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from telethon import TelegramClient
from config.config import load_config
from services.logger import log_event, log_error
from database.db_operations import init_db
from handlers import register_all_handlers
from handlers.channel_reader import set_telethon_client

async def main():

    config = load_config()
    # Initialize bot and dispatcher with new syntax
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Initialize database
    try:
        await init_db()
    except Exception as e:
        log_error(0, e, "database_init_error")
        return
    # Initialize Telethon if credentials are provided
    if config.telethon.api_id and config.telethon.api_hash:
        try:
            client = TelegramClient('channel_reader_session', 
                                  int(config.telethon.api_id), 
                                  config.telethon.api_hash)
            await client.start()
            set_telethon_client(client)
            log_event(0, "telethon_client_started")
        except Exception as e:
            log_error(0, e, "telethon_init_error")
            return
    
    # Register handlers
    register_all_handlers(dp, config)
    
    # Log bot info
    try:
        bot_info = await bot.get_me()
        log_event(0, f"bot_started_{bot_info.username}")
    except Exception as e:
        log_error(0, e, "bot_info_error")
        return
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        log_error(0, e, "polling_error")
    finally:
        log_event(0, "bot_stopped")
        if config.telethon.api_id:
            await client.disconnect()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log_event(0, "bot_stopped_by_user")
