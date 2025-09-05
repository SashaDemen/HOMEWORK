from fastapi import FastAPI, HTTPException
from typing import List
from .models import Movie, MovieCreate, MovieOut
from .store import store

app = FastAPI(title="Movies API")

@app.get("/movies", response_model=List[MovieOut])
def list_movies():
    return store.list()

@app.post("/movies", response_model=MovieOut, status_code=201)
def add_movie(data: MovieCreate):
    return store.create(data)

@app.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int):
    m = store.get(movie_id)
    if not m:
        raise HTTPException(status_code=404, detail="Movie not found")
    return m

@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int):
    ok = store.delete(movie_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Movie not found")
    return None
