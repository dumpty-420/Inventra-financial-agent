"""FastAPI routes for the AI assistant."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from langsmith import traceable
from agents.coordinator import process_query
from config.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
@traceable(name="Chat API Endpoint", tags=["production", "inventra-v1", "api-layer"])
async def chat_assistant(request: ChatRequest):
    """
    Endpoint for the Inventra AI assistant.
    Receives a query and returns the AI-generated response.
    """
    try:
        logger.info(f"Received API query: {request.query} (session_id={request.session_id})")
        
        # Process the query through the multi-agent workflow
        response = process_query(request.query, session_id=request.session_id)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Error in chat_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "inventra-assistant-api"}
