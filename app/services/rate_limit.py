from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.config import get_settings

settings = get_settings()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT]
)

def attach_rate_limit(app):
    """
    Attaches the rate limit handler and middleware to a FastAPI app
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)