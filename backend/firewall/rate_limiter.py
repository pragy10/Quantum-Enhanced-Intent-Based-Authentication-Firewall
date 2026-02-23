from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse

from config import settings
from backend.utils.redis_client import RedisClient
from backend.utils.logger import logger

class RateLimiter:
    """
    Simple IP-based rate limiter.
    Uses Redis to count requests per IP in a sliding time window.
    """
    def __init__(
        self,
        redis_client: RedisClient,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ):
        self.redis = redis_client
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW

    def _key(self, client_ip: str) -> str:
        return f"rate_limit:{client_ip}"

    async def check_rate_limit(self, client_ip: str) -> bool:
        """
        Increment counter for this IP and return:
          True  -> allowed
          False -> blocked (over limit)
        """
        key = self._key(client_ip)

        
        current = self.redis.get(key)
        if current is None:
            self.redis.set_with_expiry(key, "1", self.window_seconds)
            logger.debug(f"[RateLimiter] {client_ip}: first request in window")
            return True

        count = int(current)

        if count >= self.max_requests:
            logger.warning(
                f"[RateLimiter] {client_ip}: exceeded limit "
                f"{count}/{self.max_requests} in {self.window_seconds}s"
            )
            return False

        
        self.redis.increment(key)
        logger.debug(
            f"[RateLimiter] {client_ip}: {count+1}/{self.max_requests} "
            f"in current window"
        )
        return True

    def get_block_response(self, client_ip: str) -> JSONResponse:
        """
        HTTP 429 Too Many Requests response.
        """
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": (
                    f"Rate limit exceeded: max {self.max_requests} requests "
                    f"per {self.window_seconds} seconds"
                ),
                "client_ip": client_ip,
            },
            headers={"Retry-After": str(self.window_seconds)},
        )
    