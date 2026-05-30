from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

SECRET_PATTERNS = [re.compile(r"(api[_-]?key|token|secret)=([^\s&]+)", re.IGNORECASE)]


def sanitize_text(value: str, max_length: int = 500) -> str:
    cleaned = re.sub(r"[<>]", "", value).strip()
    return cleaned[:max_length]


def mask_secrets(value: str) -> str:
    masked = value
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub(r"\1=***", masked)
    return masked


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, limit: int = 240, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.calls: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        client = request.client.host if request.client else "local"
        now = time.time()
        calls = self.calls[client]
        while calls and calls[0] < now - self.window_seconds:
            calls.popleft()
        if len(calls) >= self.limit:
            return Response("Rate limit exceeded", status_code=429)
        calls.append(now)
        return await call_next(request)
