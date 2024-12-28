from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
from services.logger import log_event, log_error

router = Router()
POSTS_PER_REQUEST = 5

# Global variable for Telethon client
telethon_client = None

def set_telethon_client(client):
    """Set global Telethon client"""
    global telethon_client
    telethon_client = client

@router.message(Command("show_channel"))
async def show_channel(message: Message):
    """Show last 5 posts from channel"""
    user_id = message.from_user.id
    
    if telethon_client is None:
        await message.answer("Telethon client is not initialized. Add your API ID and API hash to the .env file.")
        return
        
    try:
        log_event(user_id, "channel_posts_request")

        try:
            # Get posts from channel
            channel = await telethon_client.get_entity("@telegram")
            posts = await telethon_client(GetHistoryRequest(
                peer=channel,
                limit=POSTS_PER_REQUEST,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            if not posts.messages:
                await message.answer("No posts found in this channel.")
                return

            # Format and send posts
            formatted_posts = format_posts(posts.messages, "@telegram")
            await message.answer(formatted_posts)
            
            log_event(user_id, "channel_posts_shown")

        except Exception as e:
            log_error(user_id, e, "channel_posts_fetch_error")
            await message.answer(
                "Error fetching posts. Please try again later."
            )
                
    except Exception as e:
        log_error(user_id, e, "channel_reader_error")
        await message.answer("Error processing request. Please try again later.")

def format_posts(posts: list, channel_username: str) -> str:
    """Format posts for display"""
    formatted = [f"📱 Latest posts from {channel_username}:"]
    
    for post in posts:
        # Limit text length
        text = post.message[:300] + "..." if len(post.message) > 300 else post.message
        date = post.date.strftime("%Y-%m-%d %H:%M")
        
        formatted.append(f"\n📝 Post from {date}")
        formatted.append(f"{text}\n")
        
        if post.media:
            formatted.append("🖼 [Post contains media]\n")
            
        formatted.append("-" * 30)
    
    return "\n".join(formatted) 