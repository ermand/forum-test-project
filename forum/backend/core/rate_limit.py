import os

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["80/minute"],
    enabled=os.getenv("ENV") != "test",
)
