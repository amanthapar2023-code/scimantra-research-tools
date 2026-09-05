"""Application bridge for the modular SciMantra platform.

This bridge is intentionally additive: existing Streamlit pages can import
these helpers without changing their current scientific logic. New features
should use this module instead of importing implementation details directly.
"""

from .config import APP_NAME, APP_TAGLINE, COLORS, SECTIONS
from .calculations import dilution_c1_v1_c2, molarity, normality, removal_efficiency
from .validation import require_non_empty, require_non_negative, require_positive

__all__ = [
    "APP_NAME",
    "APP_TAGLINE",
    "COLORS",
    "SECTIONS",
    "dilution_c1_v1_c2",
    "molarity",
    "normality",
    "removal_efficiency",
    "require_non_empty",
    "require_non_negative",
    "require_positive",
]
