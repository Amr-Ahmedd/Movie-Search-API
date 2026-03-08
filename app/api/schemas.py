from typing import List, Optional, Any, Literal, Dict
from pydantic import BaseModel, Field, field_validator

MovieType = Literal["movie", "series"]
TmdbMediaType = Literal["movie", "tv", "person"]

class Movie(BaseModel):
    title: str
    year: Optional[int] = None
    type: MovieType
    genre: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    source: str  # omdb / tmdb

class SearchQuery(BaseModel):
    # The same inputs the user sent
    title: Optional[str] = None
    actors: Optional[str] = None
    type: Optional[MovieType] = None
    genre: Optional[str] = None

class SearchResponse(BaseModel):
    query: SearchQuery
    count: int
    results: List[Movie]
    providers: Dict[str, bool]

class OmdbSearchItem(BaseModel):
    title: str = Field(alias="Title")
    year_raw: str | None = Field(default=None, alias="Year")
    type: str = Field(alias="Type")

    def to_movie(self) -> Movie:
        year = None
        if self.year_raw and len(self.year_raw) >= 4 and self.year_raw[:4].isdigit():
            year = int(self.year_raw[:4])

        return Movie(
            title=self.title,
            year=year,
            type=self.type,      # movie or series
            genre=[],
            actors=[],
            source="omdb"
        )

class OmdbSearchResponse(BaseModel):
    Search: list[OmdbSearchItem] = []
    Response: str | None = None
    totalResults: str | None = None

TmdbMediaType = Literal["movie", "tv", "person"]

class TmdbMultiItem(BaseModel):
    media_type: TmdbMediaType
    title: str | None = None          # movies
    name: str | None = None           # tv shows
    release_date: str | None = None   # movies
    first_air_date: str | None = None # tv shows

    def to_movie(self) -> Optional["Movie"]:
        # filter out people
        if self.media_type == "person":
            return None

        # title
        final_title = (self.title or self.name or "").strip()
        if not final_title:
            return None

        # year
        date_str = self.release_date if self.media_type == "movie" else self.first_air_date

        year = None
        if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
            year = int(date_str[:4])

        # changing type from (tv) to (series)
        final_type: MovieType = "movie" if self.media_type == "movie" else "series"

        return Movie(
            title=final_title,
            year=year,
            type=final_type,
            genre=[],
            actors=[],
            source="tmdb",
        )

class TmdbMultiResponse(BaseModel):
    results: list[TmdbMultiItem] = Field(default_factory=list)
    page: int | None = None
    total_results: int | None = None
    total_pages: int | None = None


class TmdbDiscoverItem(BaseModel):
    title: str | None = None
    name: str | None = None
    release_date: str | None = None
    first_air_date: str | None = None

    def to_movie(self, forced_type: MovieType) -> Optional["Movie"]:
        final_title = (self.title or self.name or "").strip()
        if not final_title:
            return None
        date_str = self.release_date or self.first_air_date
        year = None
        if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
            year = int(date_str[:4])
        return Movie(
            title=final_title,
            year=year,
            type=forced_type,
            genre=[],
            actors=[],
            source="tmdb",
        )

class TmdbDiscoverResponse(BaseModel):
    results: list[TmdbDiscoverItem] = Field(default_factory=list)