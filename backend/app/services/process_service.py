import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.process_navigator import get_succession_process

def get_process_steps(has_minor_heir: bool, has_dispute: bool, is_selling: bool):
    result = get_succession_process(
        has_minor_heir=has_minor_heir,
        has_dispute=has_dispute,
        is_selling=is_selling
    )
    # Return only the steps (the frontend expects a list of steps directly)
    return result.get("process_steps", [])