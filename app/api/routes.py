from typing import Optional, Literal

from fastapi import APIRouter, Query, HTTPException

from app.api.schemas import SearchResponse, OmdbSearchResponse, TmdbMultiResponse, TmdbDiscoverResponse
from app.clients.omdb_client import omdb_search_by_title, OmdbError
from app.clients.tmdb_client import tmdb_search, TmdbError , tmdb_find_person_id, tmdb_discover_by_cast, tmdb_genre_id_by_name, tmdb_discover_by_genre


router = APIRouter(prefix="/movies", tags=["movies"])

def dedupe_movies(movies):
    seen = set()
    unique = []
    for m in movies:
        key = (m.title.strip().lower(), m.year, m.type)
        if key in seen:
            continue
        seen.add(key)
        unique.append(m)
    return unique

@router.get("/search", response_model=SearchResponse)
async def search_movies(
        title: Optional[str] = Query(
            default=None, min_length=1,
            description="Search by title."
        ),
        actors: Optional[str] = Query(
            default=None, min_length=1,
            description="Search by actor name, it works without title."
        ),
        genre: Optional[str] = Query(
            default=None, min_length=1,
            description="Search by genre name, it works without title."
        ),
        type: Optional[Literal["movie", "series"]] = Query(
            default=None,
            description="Optional filter: movie or series."
        ),
):
    providers = {"omdb": True, "tmdb": True}

    if not title and not actors and not genre:
        raise HTTPException(status_code=400, detail="Provide at least one of these (title, actors, genre)")

    if actors and not title:
        try:
            person_id = await tmdb_find_person_id(actors)
            if not person_id:
                return {
                    "query": {"title": title, "actors": actors, "type": type, "genre": genre},
                    "count": 0,
                    "results": [],
                    "providers": {"omdb": False, "tmdb": True},
                }

            raw = await tmdb_discover_by_cast(person_id, type=type)
            parsed = TmdbDiscoverResponse.model_validate(raw)

            forced_type = "series" if type == "series" else "movie"

            tmdb_movies = []
            for it in parsed.results:
                movie = it.to_movie(forced_type)
                if movie is not None:
                    tmdb_movies.append(movie)

            tmdb_movies = dedupe_movies(tmdb_movies)
            return {
                "query": {"title": title, "actors": actors, "type": type, "genre": genre},
                "count": len(tmdb_movies),
                "results": tmdb_movies,
                "providers": {"omdb": False, "tmdb": True},
            }
        except TmdbError:
            raise HTTPException(status_code=502, detail="TMDB provider failed")

    if genre and not title:
        try:
            gid = await tmdb_genre_id_by_name(genre, type=type)
            if not gid:
                return {
                    "query": {"title": title, "actors": actors, "type": type, "genre": genre},
                    "count": 0,
                    "results": [],
                    "providers": {"omdb": False, "tmdb": True},
                }

            raw = await tmdb_discover_by_genre(gid, type=type)
            parsed = TmdbDiscoverResponse.model_validate(raw)

            forced_type = "series" if type == "series" else "movie"

            tmdb_movies = []
            for it in parsed.results:
                movie = it.to_movie(forced_type)
                if movie is not None:
                    tmdb_movies.append(movie)

            tmdb_movies = dedupe_movies(tmdb_movies)
            return {
                "query": {"title": title, "actors": actors, "type": type, "genre": genre},
                "count": len(tmdb_movies),
                "results": tmdb_movies,
                "providers": {"omdb": False, "tmdb": True},
            }
        except TmdbError:
            raise HTTPException(status_code=502, detail="TMDB provider failed")

    # Call OMDb
    omdb_movies = []
    try:
        omdb_raw = await omdb_search_by_title(title=title, type=type)
        omdb_parsed = OmdbSearchResponse.model_validate(omdb_raw)
        for item in omdb_parsed.Search:
            movie = item.to_movie()
            omdb_movies.append(movie)
    except OmdbError:
        omdb_movies = []
        providers["omdb"] = False

    # Call TMDB
    tmdb_movies = []
    try:
        tmdb_raw = await tmdb_search(title=title)
        tmdb_parsed = TmdbMultiResponse.model_validate(tmdb_raw)
        for item in tmdb_parsed.results:
            movie = item.to_movie()
            if movie is not None:
                tmdb_movies.append(movie)
    except TmdbError:
        tmdb_movies = []
        providers["tmdb"] = False

    if not providers["omdb"] and not providers["tmdb"]:
        raise HTTPException(status_code=502, detail="Both providers failed")

    merged = omdb_movies + tmdb_movies

    if type:
        filtered = []
        for movie in merged:
            if movie.type == type:
                filtered.append(movie)
        merged = filtered

    merged = dedupe_movies(merged)

    return {
        "query": {"title": title, "actors": actors, "type": type, "genre": genre},
        "count": len(merged),
        "results": merged,
        "providers": providers,
    }

