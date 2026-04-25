from pydantic import BaseModel

class NLPRequest(BaseModel):
    text: str

class NLPResponse(BaseModel):
    raw: dict
    normalized: dict
    method: str
