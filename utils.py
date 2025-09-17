import time
from typing import Dict
from config import RATE_LIMIT_PER_MINUTE

# Simple in-memory rate-limit tracker (works across process lifetime; for Heroku multiple dynos it's not global)
# We also track via DB message counts (database.record_message + count_messages_last_minute) in handlers.
_rate_limits: Dict[int, list] = {}

def allowed_by_inmemory_rate(user_id: int) -> bool:
    """
    Basic sliding window using timestamps in list.
    Keep timestamps for last 60 seconds.
    """
    now = time.time()
    window_start = now - 60
    arr = _rate_limits.get(user_id, [])
    # drop old
    arr = [t for t in arr if t >= window_start]
    if len(arr) >= RATE_LIMIT_PER_MINUTE:
        _rate_limits[user_id] = arr
        return False
    arr.append(now)
    _rate_limits[user_id] = arr
    return True
