from typing import Any, Dict, Optional, Literal
import httpx
from app.core.config import settings

TmdbDiscoverType = Optional[Literal["movie", "series"]]

class TmdbError(Exception):
    pass

TMDB_BASE = "https://api.themoviedb.org/3"

async def tmdb_search(title: str) -> Dict[str, Any]:
    if not settings.tmdb_api_key:
        raise TmdbError("TMDB_API_KEY is missing")

    params = {
        "api_key": settings.tmdb_api_key,
        "query": title,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TMDB_BASE}/search/multi", params=params)

    if resp.status_code != 200:
        raise TmdbError(f"TMDB HTTP error: {resp.status_code} - {resp.text}")

    return resp.json()


async def tmdb_find_person_id(person_name: str) -> Optional[int]:
    params = {
        "api_key": settings.tmdb_api_key,
        "query": person_name,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TMDB_BASE}/search/person", params=params)

    if resp.status_code != 200:
        raise TmdbError(f"TMDB HTTP error: {resp.status_code} - {resp.text}")

    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None # actor not found.
    return results[0].get("id")


async def tmdb_discover_by_cast(person_id: int, type: TmdbDiscoverType = None) -> Dict[str, Any]:
    endpoint = "movie" if type != "series" else "tv"
    params = {
        "api_key": settings.tmdb_api_key,
        "with_cast": person_id,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": "popularity.desc",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TMDB_BASE}/discover/{endpoint}", params=params)

    if resp.status_code != 200:
        raise TmdbError(f"TMDB HTTP error: {resp.status_code} - {resp.text}")

    return resp.json()


async def tmdb_genre_id_by_name(genre_name: str, type: TmdbDiscoverType = None) -> Optional[int]:
    endpoint = "movie" if type != "series" else "tv"
    params = {"api_key": settings.tmdb_api_key,
              "language": "en-US"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TMDB_BASE}/genre/{endpoint}/list", params=params)

    if resp.status_code != 200:
        raise TmdbError(f"TMDB HTTP error: {resp.status_code} - {resp.text}")

    genres = resp.json().get("genres", [])
    g = genre_name.strip().lower()
    for item in genres:
        if str(item.get("name", "")).strip().lower() == g:
            return item.get("id")
    return None


async def tmdb_discover_by_genre(genre_id: int, type: TmdbDiscoverType = None) -> Dict[str, Any]:
    endpoint = "movie" if type != "series" else "tv"
    params = {
        "api_key": settings.tmdb_api_key,
        "with_genres": genre_id,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": "popularity.desc",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TMDB_BASE}/discover/{endpoint}", params=params)

    if resp.status_code != 200:
        raise TmdbError(f"TMDB HTTP error: {resp.status_code} - {resp.text}")

    return resp.json()