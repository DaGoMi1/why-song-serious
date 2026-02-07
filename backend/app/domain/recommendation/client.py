import httpx
from fastapi import HTTPException, status

from app.config import get_settings

AI_REQUEST_TIMEOUT = 10.0


async def request_model_recommendation(
    model_type: str,
    spotify_track_ids: list[str],
) -> list[dict]:
    settings = get_settings()
    url = f"{settings.ai_service_url}/ai/recommendations"

    payload = {
        "model_type": model_type,
        "seed_song_ids": spotify_track_ids,
    }

    try:
        async with httpx.AsyncClient(timeout=AI_REQUEST_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service request timed out",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.response.status_code}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service is unavailable",
        )

    body = response.json()
    return body["data"]
