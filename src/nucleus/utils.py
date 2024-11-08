import time
import logging
import functools
from typing import Any, Callable, TypeVar, Optional
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger("nucleus")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

T = TypeVar('T')

class RateLimit:
    """Rate limiting implementation."""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            now = datetime.now()
            self.timestamps = [ts for ts in self.timestamps if now - ts < timedelta(seconds=self.period)]
            
            if len(self.timestamps) >= self.calls:
                sleep_time = (self.timestamps[0] + timedelta(seconds=self.period) - now).total_seconds()
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
            
            self.timestamps.append(now)
            return func(*args, **kwargs)
        return wrapper

class Cache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.ttl):
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cache set for key: {key}")

def retry(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    wait_time = delay * (2 ** (retries - 1))  # exponential backoff
                    logger.warning(f"Retry {retries}/{max_retries} after error: {str(e)}. "
                                 f"Waiting {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
            return func(*args, **kwargs)  # one last try
        return wrapper
    return decorator
