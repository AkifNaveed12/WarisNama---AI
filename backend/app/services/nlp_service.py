import sys
from app.core.config import settings
if str(settings.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(settings.BASE_DIR))

from ai.nlp_parser import parse_scenario as original_parse

def parse_natural_language(text: str) -> dict:
    """Return raw+normalized+method."""
    return original_parse(text)
