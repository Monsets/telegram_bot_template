import os
from os import getenv
from dataclasses import dataclass
from dotenv import dotenv_values
from pathlib import Path
from typing import Optional

SUBSCRIPTION_PLANS = {
    "1month": {
        "title": "1 Month",
        "description": "Access for one month",
        "price": 1,
        "days": 30,
    },
    "3months": {
        "title": "3 Months",
        "description": "Access for three months",
        "price": 2,
        "days": 90,
    },
    "6months": {
        "title": "6 Months",
        "description": "Access for six months",
        "price": 3,
        "days": 180,
    },
    "1year": {
        "title": "1 Year",
        "description": "Access for one year",
        "price": 4,
        "days": 365,
    }
} 

@dataclass
class BotConfig:
    token: str

@dataclass
class TelethonConfig:
    api_id: Optional[str]
    api_hash: Optional[str]
    channel_username: str

@dataclass
class Config:
    bot: BotConfig
    telethon: TelethonConfig

def load_config(env_path: str = '.env') -> Config:
    # Загружаем переменные напрямую
    config_values = dotenv_values('.env')
    
    bot_token = config_values.get('BOT_TOKEN')
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in .env file")

    return Config(
        bot=BotConfig(
            token=bot_token
        ),
        telethon=TelethonConfig(
            api_id=config_values.get("TELETHON_API_ID"),
            api_hash=config_values.get("TELETHON_API_HASH"),
            channel_username=config_values.get("CHANNEL_USERNAME", "@telegram")
        ),
    )
