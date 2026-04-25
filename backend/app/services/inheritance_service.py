import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
from app.core.config import settings
if str(settings.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(settings.BASE_DIR))

from core.faraid_engine import calculate_shares as original_calculate_shares

def calculate_inheritance(
    sect: str,
    heirs: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0,
    wasiyyat: float = 0,
    predeceased_sons: Optional[list] = None
) -> Dict[str, Any]:
    """
    Wrapper around core.faraid_engine.calculate_shares.
    Returns the same dictionary.
    """
    try:
        result = original_calculate_shares(
            sect=sect,
            heirs=heirs,
            total_estate=total_estate,
            debts=debts,
            funeral=funeral,
            wasiyyat=wasiyyat,
            predeceased_sons=predeceased_sons
        )
        return result
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}
