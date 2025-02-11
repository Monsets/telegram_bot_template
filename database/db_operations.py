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
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                referrer_id INTEGER,
                referral_count INTEGER
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

async def add_user(user_id: int, username: str, name: str, referrer_id: Optional[int] = None):
    """Add new user to database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, name, created_at, referrer_id, referral_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, username, name, datetime.now(), referrer_id, 0)
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
                is_active=bool(user_data[5]),
                referrer_id=user_data[6],
                referral_count=user_data[7]
            )

# Subscription operations
async def create_subscription(user_id: int, subscription_type: str, start_date: datetime, end_date: datetime):
    """Create or extend subscription"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # First, check if user has active subscription
        current_sub = await get_active_subscription(user_id)
        
        if current_sub:
            # If subscription exists, extend it
            new_end_date = max(current_sub.end_date, start_date) + (end_date - start_date)
            query = """
                UPDATE subscriptions 
                SET end_date = $1 
                WHERE user_id = $2 AND is_active = true
            """
            await db.execute(query, (new_end_date, user_id))
        else:
            # If no subscription, create new one
            query = """
                INSERT INTO subscriptions (user_id, subscription_type, start_date, end_date, is_active)
                VALUES ($1, $2, $3, $4, $5)
            """
            await db.execute(query, (user_id, subscription_type, start_date, end_date, True))
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

async def update_referral_count(user_id: int):
    """Increment referral count for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE users 
            SET referral_count = referral_count + 1 
            WHERE user_id = ?
            """,
            (user_id,)
        )
        await db.commit()

async def get_active_users() -> List[User]:
    """Get all active users"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE is_active = TRUE"
        ) as cursor:
            users = await cursor.fetchall()
            return [
                User(
                    id=user[0],
                    user_id=user[1],
                    username=user[2],
                    name=user[3],
                    created_at=datetime.fromisoformat(user[4]),
                    is_active=bool(user[5]),
                    referrer_id=user[6],
                    referral_count=user[7]
                ) for user in users
            ]
