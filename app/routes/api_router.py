from fastapi import APIRouter
import httpx

api_router = APIRouter()

@api_router.get("/ping")
async def ping():
    return {"status": "ok"}

@api_router.get("/channel_info")
async def channel_info(username: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/channel_check",
                json={"channel_identifier": username}
                )

            return response.json()
    except Exception as e:
        return {"error": str(e)}
