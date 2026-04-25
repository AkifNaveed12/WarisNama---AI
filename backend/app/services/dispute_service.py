import sys
from app.core.config import settings
if str(settings.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(settings.BASE_DIR))

from core.dispute_detector import detect_inheritance_disputes

def detect_disputes(dispute_flags: dict) -> dict:
    """Wrapper for dispute detection."""
    return detect_inheritance_disputes(dispute_flags)
