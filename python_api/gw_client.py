import httpx
import logging
from fastapi import HTTPException

gw_URL = "http://localhost:8080" # Go Gateway address

async def publish_event(room: str, event_type: str, payload: dict, db_session) -> str:
    """
    Publishes event to Go Gateway. 
    Returns 'ok' or 'degraded' if Gateway is down.
    """
    event_data = {
        "room": room,
        "event_type": event_type,
        "payload": payload
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Service token should be passed here in production
            headers = {"Authorization": "Bearer SERVICE_TOKEN"} 
            resp = await client.post(f"{gw_URL}/api/v1/events", json=event_data, headers=headers, timeout=2.0)
            resp.raise_for_status()
            return "ok"
    except Exception as e:
        logging.warning(f"Gateway unavailable, falling back to degraded mode: {e}")
        return "degraded"