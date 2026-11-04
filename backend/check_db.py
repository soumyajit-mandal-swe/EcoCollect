"""Quiet readiness probe compatible with Windows PowerShell."""
import sys

try:
    from sqlalchemy import text
    from .database import engine
    with engine.connect() as connection:
        connection.execute(text('SELECT 1'))
except Exception:
    sys.exit(1)
