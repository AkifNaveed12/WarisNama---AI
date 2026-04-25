from fastapi import APIRouter
from app.api.v1.routes import (
    inheritance_routes,
    nlp_routes,
    dispute_routes,
    tax_routes,
    document_routes
)

api_router = APIRouter()
api_router.include_router(inheritance_routes.router)
api_router.include_router(nlp_routes.router)
api_router.include_router(dispute_routes.router)
api_router.include_router(tax_routes.router)
api_router.include_router(document_routes.router)
from app.api.v1.routes import chat_routes
api_router.include_router(chat_routes.router)
from app.api.v1.routes import process_routes
api_router.include_router(process_routes.router)
from app.api.v1.routes import verify_routes
api_router.include_router(verify_routes.router)