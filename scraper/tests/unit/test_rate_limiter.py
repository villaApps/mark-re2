"""Tests for rate limiter."""

import asyncio
import pytest

from src.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_within_limit(self):
        """Test that rate limiter allows requests within limit."""
        limiter = RateLimiter(calls=3, period=1.0)
        
        # Should not block for first 3 calls
        start = asyncio.get_event_loop().time()
        
        async with limiter:
            pass
        async with limiter:
            pass
        async with limiter:
            pass
        
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed < 0.1  # Should be almost instant
    
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_when_exceeded(self):
        """Test that rate limiter blocks when limit exceeded."""
        limiter = RateLimiter(calls=1, period=0.5)
        
        # First call
        async with limiter:
            pass
        
        # Second call should block
        start = asyncio.get_event_loop().time()
        async with limiter:
            pass
        elapsed = asyncio.get_event_loop().time() - start
        
        assert elapsed >= 0.4  # Should have waited ~0.5s
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_direct(self):
        """Test direct acquire method."""
        limiter = RateLimiter(calls=2, period=1.0)
        
        await limiter.acquire()
        await limiter.acquire()
        
        # Should have 2 timestamps recorded
        assert len(limiter.timestamps) == 2
    
    @pytest.mark.asyncio
    async def test_rate_limiter_clears_old_timestamps(self):
        """Test that old timestamps are cleared."""
        limiter = RateLimiter(calls=1, period=0.1)
        
        # First call
        async with limiter:
            pass
        
        # Wait for period to expire
        await asyncio.sleep(0.15)
        
        # Second call should not block
        start = asyncio.get_event_loop().time()
        async with limiter:
            pass
        elapsed = asyncio.get_event_loop().time() - start
        
        assert elapsed < 0.1  # Should not have blocked
