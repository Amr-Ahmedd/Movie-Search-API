from typing import Optional, Literal, Any, Dict
import httpx

from app.core.config import settings

OmdbType = Optional[Literal["movie", "series"]]


class OmdbError(Exception):
    """Raised when OMDb request fails or returns an error response"""


async def omdb_search_by_title(title: str, type: OmdbType = None) -> Dict[str, Any]:

    if not settings.omdb_api_key:
        raise OmdbError("OMDB_API_KEY is missing")

    params = {"apikey": settings.omdb_api_key, "s": title}
    if type:
        params["type"] = type

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://www.omdbapi.com/", params=params)

    if resp.status_code != 200:
        raise OmdbError(f"OMDb HTTP error: {resp.status_code}")

    data = resp.json()

    if data.get("Response") == "False":
        raise OmdbError(data.get("Error", "OMDb returned an error"))

    return data