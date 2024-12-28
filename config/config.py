from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv
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

def load_config() -> Config:
    load_dotenv('.env')

    return Config(
        bot=BotConfig(
            token=getenv("BOT_TOKEN")
        ),
        telethon=TelethonConfig(
            api_id=getenv("TELETHON_API_ID"),
            api_hash=getenv("TELETHON_API_HASH"),
            channel_username=getenv("CHANNEL_USERNAME", "@telegram")
        ),
    )
