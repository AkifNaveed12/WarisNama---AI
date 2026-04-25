from fastapi import APIRouter, HTTPException
from app.schemas.inheritance_schemas import CalculationRequest, CalculationResponse
from app.services.inheritance_service import calculate_inheritance

router = APIRouter(prefix="/calculate", tags=["Inheritance"])

@router.post("/", response_model=dict)
async def calculate_shares(request: CalculationRequest):
    """
    Calculate inheritance shares based on sect, heirs, and estate details.
    """
    # Convert Pydantic heirs to dict (skip zero values)
    heirs_dict = request.heirs.dict(exclude_unset=True, exclude_none=True)
    # Filter out keys that are zero
    heirs_dict = {k: v for k, v in heirs_dict.items() if v != 0}

    result = calculate_inheritance(
        sect=request.sect,
        heirs=heirs_dict,
        total_estate=request.total_estate,
        debts=request.debts,
        funeral=request.funeral,
        wasiyyat=request.wasiyyat,
        predeceased_sons=request.predeceased_sons
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Convert shares to Pydantic-friendly dict
    shares_dict = result.get("shares", {})
    formatted_shares = {}
    for heir_id, share_data in shares_dict.items():
        formatted_shares[heir_id] = {
            "fraction": share_data.get("fraction"),
            "amount": share_data.get("amount"),
            "reference": share_data.get("reference"),
            "note": share_data.get("note")
        }

    return {
        "status": "success",
        "data": {
            "distributable_estate": result.get("distributable_estate"),
            "warning": result.get("warning"),
            "shares": formatted_shares
        }
    }
