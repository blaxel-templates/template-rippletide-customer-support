import uuid
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from blaxel.telemetry.span import SpanManager

router = APIRouter()

# Hardcoded API key - update this with your API key from https://eval.rippletide.com
RIPPLETIDE_API_KEY = "your-api-key-here"
# Hardcoded Agent ID - update this with your agent ID
RIPPLETIDE_AGENT_ID = "your-agent-id-here"
# Base URL for Rippletide API
RIPPLETIDE_BASE_URL = "https://agent.rippletide.com/api/sdk"

class RequestInput(BaseModel):
    inputs: str

@router.post("/")
async def handle_request(request: Request):
    if RIPPLETIDE_API_KEY == "your-api-key-here":
        raise HTTPException(status_code=500, detail="RIPPLETIDE_API_KEY is not configured. Please update it in agent.py")
    if RIPPLETIDE_AGENT_ID == "your-agent-id-here":
        raise HTTPException(status_code=500, detail="RIPPLETIDE_AGENT_ID is not configured. Please update it in agent.py")

    body = RequestInput(**await request.json())

    # Get or generate conversation UUID
    conversation_uuid = request.headers.get("X-Conversation-UUID")
    if not conversation_uuid:
        conversation_uuid = str(uuid.uuid4())

    with SpanManager("blaxel-rippletide-customer-support").create_active_span("agent-request", {}):
        url = f"{RIPPLETIDE_BASE_URL}/chat/{RIPPLETIDE_AGENT_ID}"
        
        headers = {
            "x-api-key": RIPPLETIDE_API_KEY,
            "Content-Type": "application/json",
            "x-rippletide-agent-id": str(RIPPLETIDE_AGENT_ID),
            "x-rippletide-conversation-id": conversation_uuid,
        }
        
        payload = {
            "user_message": body.inputs,
            "conversation_uuid": conversation_uuid
        }
        
        async with httpx.AsyncClient(timeout=360.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
        
        answer_text = response_data.get("answer", "No answer provided")
        return PlainTextResponse(content=answer_text)