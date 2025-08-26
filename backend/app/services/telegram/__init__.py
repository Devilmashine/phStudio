"""
Telegram Integration Package

This package contains the refactored Telegram integration system.
"""

# Import modules but not instances to avoid initialization issues
from . import template_engine
from . import service

__all__ = [
    "template_engine",
    "service"
]