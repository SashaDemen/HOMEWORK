from threading import Lock
from typing import Dict, List, Optional
from .models import Movie, MovieCreate

class MovieStore:
    def __init__(self):
        self._by_id: Dict[int, Movie] = {}
        self._lock = Lock()
        self._next_id = 1

    def list(self) -> List[Movie]:
        return list(self._by_id.values())

    def create(self, data: MovieCreate) -> Movie:
        with self._lock:
            mid = self._next_id
            self._next_id += 1
            m = Movie(id=mid, **data.model_dump())
            self._by_id[mid] = m
            return m

    def get(self, movie_id: int) -> Optional[Movie]:
        return self._by_id.get(movie_id)

    def delete(self, movie_id: int) -> bool:
        with self._lock:
            return self._by_id.pop(movie_id, None) is not None

store = MovieStore()
