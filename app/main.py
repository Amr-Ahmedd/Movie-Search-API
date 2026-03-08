from fastapi import FastAPI
from app.api.routes import router as movies_router
from app.core.config import settings

print("OMDB key loaded:", bool(settings.omdb_api_key))
print("TMDB key loaded:", bool(settings.tmdb_api_key))

app = FastAPI(title="Movie Search API")

@app.get("/health")
def health():
    return {"status": "ok"}
app.include_router(movies_router)

