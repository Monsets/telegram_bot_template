from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    user_id: int
    username: Optional[str]
    name: Optional[str]
    created_at: datetime
    is_active: bool = True

@dataclass
class Subscription:
    id: int
    user_id: int
    subscription_type: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
