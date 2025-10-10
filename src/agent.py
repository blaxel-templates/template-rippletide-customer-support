import os
import uuid
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from blaxel.telemetry.span import SpanManager

router = APIRouter()

class RequestInput(BaseModel):
    inputs: str

@router.post("/")
async def handle_request(request: Request):
    base_url = os.getenv("BASE_URL", "https://agent.rippletide.com/api/sdk")
    api_key = os.getenv("RIPPLETIDE_API_KEY")
    body = RequestInput(**await request.json())
    if api_key is None:
        raise HTTPException(status_code=500, detail="RIPPLETIDE_API_KEY is not set")
    agent_id = os.getenv("RIPPLETIDE_AGENT_ID")
    if agent_id is None:
        raise HTTPException(status_code=500, detail="RIPPLETIDE_AGENT_ID is not set")

    # Get or generate conversation UUID
    conversation_uuid = request.headers.get("X-Conversation-UUID")
    if not conversation_uuid:
        conversation_uuid = str(uuid.uuid4())

    with SpanManager("blaxel-rippletide-customer-support").create_active_span("agent-request", {}):
        url = f"{base_url}/chat/{agent_id}"

        # Prepare headers with API key
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

        # Prepare the request payload
        payload = {
            "user_message": body.inputs,
            "conversation_uuid": conversation_uuid
        }

        # Use async httpx client with timeout
        async with httpx.AsyncClient(timeout=360.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                response_data = response.json()
                # Return just the answer text as plain text instead of JSON
                answer_text = response_data.get("answer", "No answer provided")
                return PlainTextResponse(content=answer_text)
            except httpx.HTTPStatusError as e:
                # Include response body for better error debugging
                error_detail = f"{str(e)}"
                if e.response.text:
                    error_detail += f" - {e.response.text}"
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
            except httpx.RequestError as e:
                error_msg = f"Request error: {type(e).__name__}: {str(e)}"
                raise HTTPException(status_code=500, detail=error_msg)