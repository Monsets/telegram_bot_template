import aiosqlite
from datetime import datetime
from typing import Optional, List
from .models import User, Subscription
from services.logger import log_event, log_error
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "bot.db"

async def init_db():
    """Initialize database and create tables if they don't exist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                name TEXT,
                created_at TIMESTAMP NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            )
        """)

        # Create subscriptions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_type TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        await db.commit()

async def add_user(user_id: int, username: Optional[str] = None, 
                  name: Optional[str] = None) -> None:
    """Add new user to database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        created_at = datetime.now()
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, username, name, created_at)
        )
        await db.commit()

async def get_user(user_id: int) -> Optional[User]:
    """Get user by user_id"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            user_data = await cursor.fetchone()
            
            if user_data is None:
                return None
                
            return User(
                id=user_data[0],
                user_id=user_data[1],
                username=user_data[2],
                name=user_data[3],
                created_at=datetime.fromisoformat(user_data[4]),
                is_active=bool(user_data[5])
            )

# Subscription operations
async def create_subscription(user_id: int, subscription_type: str, 
                           start_date: datetime, end_date: datetime) -> None:
    """Create new subscription"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO subscriptions (user_id, subscription_type, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, subscription_type, start_date, end_date)
        )
        await db.commit()

async def cancel_subscription(user_id: int) -> None:
    """Cancel all active subscriptions for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE subscriptions 
            SET is_active = FALSE 
            WHERE user_id = ? AND is_active = TRUE
            """,
            (user_id,)
        )
        await db.commit()

async def extend_subscription(subscription_id: int, new_end_date: datetime) -> None:
    """Extend subscription end date"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE subscriptions 
            SET end_date = ? 
            WHERE id = ? AND is_active = TRUE
            """,
            (new_end_date, subscription_id)
        )
        await db.commit()

async def get_active_subscription(user_id: int) -> Optional[Subscription]:
    """Get active subscription for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            """
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND is_active = TRUE AND end_date > ?
            ORDER BY end_date DESC LIMIT 1
            """,
            (user_id, datetime.now())
        ) as cursor:
            sub_data = await cursor.fetchone()
            
            if sub_data is None:
                return None
                
            return Subscription(
                id=sub_data[0],
                user_id=sub_data[1],
                subscription_type=sub_data[2],
                start_date=datetime.fromisoformat(sub_data[3]),
                end_date=datetime.fromisoformat(sub_data[4]),
                is_active=bool(sub_data[5])
            )
