import sys
from app.core.config import settings
if str(settings.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(settings.BASE_DIR))

from core.tax_engine import calculate_all_heirs_tax as original_calculate_tax
from core.knowledge_base import Province, FilerStatus

def calculate_taxes(
    heirs_shares: dict,
    full_property_value_pkr: float,
    filer_status_map: dict = None,
    action: str = "sell",
    province: str = Province.DEFAULT
) -> dict:
    if filer_status_map is None:
        # default: all heirs as NON_FILER
        filer_status_map = {h: FilerStatus.NON_FILER for h in heirs_shares}
    return original_calculate_tax(
        heirs_shares=heirs_shares,
        filer_status_map=filer_status_map,
        full_property_value_pkr=full_property_value_pkr,
        action=action,
        province=province
    )
