from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from database.db_operations import get_active_users
import asyncio

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_mass_notification(
        self,
        text: str,
        exclude_users: Optional[List[int]] = None,
        delay: float = 0.05
    ) -> dict:
        """
        Send notification to all active users
        
        Args:
            text: Message text to send
            exclude_users: List of user IDs to exclude from notification
            delay: Delay between messages in seconds to avoid flood limits
            
        Returns:
            dict with statistics about sending results
        """
        exclude_users = exclude_users or []
        stats = {
            "total": 0,
            "sent": 0,
            "failed": 0,
            "excluded": len(exclude_users)
        }

        try:
            users = await get_active_users()
            stats["total"] = len(users)

            for user in users:
                if user.user_id in exclude_users:
                    continue

                try:
                    await self.bot.send_message(user.user_id, text)
                    stats["sent"] += 1
                except TelegramBadRequest as e:
                    stats["failed"] += 1
                except Exception:
                    stats["failed"] += 1

                await asyncio.sleep(delay)

        except Exception:
            raise

        return stats

    async def send_notification_to_users(
        self,
        user_ids: List[int],
        text: str,
        delay: float = 0.05
    ) -> dict:
        """
        Send notification to specific users
        
        Args:
            user_ids: List of user IDs to send notification to
            text: Message text to send
            delay: Delay between messages in seconds
            
        Returns:
            dict with statistics about sending results
        """
        stats = {
            "total": len(user_ids),
            "sent": 0,
            "failed": 0
        }

        for user_id in user_ids:
            try:
                await self.bot.send_message(user_id, text)
                stats["sent"] += 1
            except Exception:
                stats["failed"] += 1

            await asyncio.sleep(delay)

        return stats 