"""
ECG Insight Mentor Backend - Main package.
"""

__version__ = "1.0.0"

# Import app only when needed (avoid circular imports in scripts)
try:
    from app.main import app
    __all__ = ["app"]
except ImportError:
    __all__ = []
