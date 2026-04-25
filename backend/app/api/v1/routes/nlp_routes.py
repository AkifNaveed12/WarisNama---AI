from fastapi import APIRouter, HTTPException
from app.schemas.nlp_schemas import NLPRequest, NLPResponse
from app.services.nlp_service import parse_natural_language

router = APIRouter(prefix="/nlp", tags=["NLP"])

@router.post("/parse")
async def parse_scenario(request: NLPRequest):
    try:
        result = parse_natural_language(request.text)
        return {
            "status": "success",
            "data": {
                "raw": result.get("raw"),
                "normalized": result.get("normalized"),
                "method": result.get("method")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
