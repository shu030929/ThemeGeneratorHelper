"""User theme builder MVP.

This package generates iOS .ktheme files and Android resource zips from a
platform-neutral theme JSON document.
"""

from .models import DEFAULT_THEME, merge_theme, validate_theme

__all__ = ["DEFAULT_THEME", "merge_theme", "validate_theme"]
__version__ = "0.1.0"
