import httpx

async def check_channel_access_http(channel_identifier: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "http://localhost:8001/channel_check",
                json={
                    "channel_identifier": channel_identifier
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"access_status": "ERROR", "error": f"Ошибка сервера: {e.response.status_code}"}
    except httpx.RequestError as e:
        return {"access_status": "ERROR", "error": f"Сетевой сбой: {str(e)}"}
