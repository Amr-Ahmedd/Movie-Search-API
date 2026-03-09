# 🎬 Movie Search API (FastAPI)

A RESTful Movie Search API built with **FastAPI** and **Pydantic**.  It aggregates results from **two public movie providers** and returns a **unified JSON structure** regardless of provider:
- **OMDb API** 
- **TMDB API** 

---

## Features

### Supported search modes
`GET /movies/search` supports:

1. **Title search**
   - `?title=batman`
2. **Actor-only search** (no title needed)
   - `?actors=Christian Bale`
3. **Genre-only search** (no title needed)
   - `?genre=Action`

###  Filters
- `type`: optional filter (`movie` or `series`)
  - In actor-only / genre-only mode: if `type` is omitted, the API defaults to **movie**.

---

## 🚀 Tech Stack
- FastAPI
- Pydantic
- httpx

---

## ▶️ Setup & Run

### 1) Create and activate a virtual environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Create .env (API keys)
```bash
OMDB_API_KEY=YOUR_OMDB_KEY
TMDB_API_KEY=YOUR_TMDB_KEY
```

### 4) Run the server
```bash
uvicorn app.main:app --reload
```
---

## API Key Setup

### OMDb API Key
- Request a free API key from **OMDb**.
- Add it to your `.env` file as:
  ```env
  OMDB_API_KEY=YOUR_OMDB_KEY

### TMDB API Key
- Create a **TMDB** account and generate an API key (v3)
- Add it to your `.env` file as:
  ```env
  TMDB_API_KEY=YOUR_TMDB_KEY

>⚠️ **Note:** This project uses the **v3 API key**, **not** the v4 bearer token.
---

## API Reference
### `GET /movies/search`

Search movies/series by **title** OR **actors** OR **genre**.

### Query Parameters

- **title** (`string`, optional): Title keyword search.
- **actors** (`string`, optional): Actor name search, works without title.
- **genre** (`string`, optional): Genre name search, works without title.
- **type** (`string`, optional): Allowed values: `movie` or `series`.
  
## Examples

## 1) Title search 

```bash
curl "http://127.0.0.1:8000/movies/search?title=batman"
```
## 2) Title search with type filter

### Movie
```bash
curl "http://127.0.0.1:8000/movies/search?title=batman&type=movie"
```
### Series
```bash
curl "http://127.0.0.1:8000/movies/search?title=batman&type=series"
```

## 3) Actor-only search 

```bash
curl "http://127.0.0.1:8000/movies/search?actors=Christian%20Bale"
```

## 4) Genre-only search 

```bash
curl "http://127.0.0.1:8000/movies/search?genre=Action"
```

## Response Format (200)

```json
{
  "query": {
    "title": "batman",
    "actors": null,
    "type": "movie",
    "genre": null
  },
  "count": 20,
  "results": [
    {
      "title": "Batman Begins",
      "year": 2005,
      "type": "movie",
      "genre": [],
      "actors": [],
      "source": "omdb"
    }
  ],
  "providers": {
    "omdb": true,
    "tmdb": true
  }
}


