"""Rate limiting utilities for scrapers."""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Simple async rate limiter."""
    
    def __init__(self, calls: int, period: float):
        """Initialize rate limiter.
        
        Args:
            calls: Number of calls allowed
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.timestamps: list[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request.
        
        Blocks if rate limit would be exceeded.
        """
        async with self._lock:
            now = time.time()
            
            # Remove timestamps outside the period
            cutoff = now - self.period
            self.timestamps = [ts for ts in self.timestamps if ts > cutoff]
            
            # Check if we need to wait
            if len(self.timestamps) >= self.calls:
                # Wait until the oldest timestamp expires
                sleep_time = self.timestamps[0] + self.period - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Recalculate after sleep
                    now = time.time()
                    cutoff = now - self.period
                    self.timestamps = [ts for ts in self.timestamps if ts > cutoff]
            
            # Record this call
            self.timestamps.append(now)
    
    async def __aenter__(self) -> "RateLimiter":
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        pass
