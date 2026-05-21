import time
from collections import defaultdict, deque

import redis
from fastapi import HTTPException, Request, status

from app.config import get_settings


class RateLimiter:
    def __init__(self) -> None:
        settings = get_settings()
        self.window_seconds = settings.rate_limit_window_seconds
        self.max_requests = settings.rate_limit_max_requests
        self.memory_hits: dict[str, deque[float]] = defaultdict(deque)
        self.redis_client: redis.Redis | None = None
        if settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None

    def check(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate-limit:create:{client_ip}"
        if self.redis_client:
            count = self.redis_client.incr(key)
            if count == 1:
                self.redis_client.expire(key, self.window_seconds)
            if count > self.max_requests:
                raise_rate_limit()
            return

        now = time.time()
        hits = self.memory_hits[key]
        while hits and hits[0] <= now - self.window_seconds:
            hits.popleft()
        if len(hits) >= self.max_requests:
            raise_rate_limit()
        hits.append(now)


def raise_rate_limit() -> None:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many short links created. Please wait and try again.",
    )


rate_limiter = RateLimiter()
