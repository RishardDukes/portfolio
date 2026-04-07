"""Shared Flask extension instances.

Imported by the app factory (__init__.py) for initialisation AND by blueprints
that need access to the limiter (e.g. auth.py). Keeping them here breaks the
circular-import that would occur if blueprints imported directly from __init__.
"""
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],           # no global limit; apply per-route
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)
